from __future__ import annotations

import dataclasses
import typing
from typing import Literal, Mapping, Sequence

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.path import AbsolutePath
from pulumi import Input, Output, Resource, ResourceOptions
from pydantic import Field, PositiveInt

from ...extract.global_ import GlobalExtractor
from .database import ContainerDatabaseConfig
from .docker_socket import ContainerDockerSocketConfig
from .healthcheck import ContainerHealthCheckConfig
from .host import ContainerHostConfig
from .image import ContainerImageModelConfig
from .inherit import ContainerInheritConfig
from .mail import ContainerMailConfig
from .network import ContainerNetworkConfig
from .port import ContainerPortConfig
from .ports import ContainerPortsConfig
from .tmpfs import ContainerTmpfsConfig
from .volume import ContainerVolumeConfig, ContainerVolumesConfig
from .wud import ContainerWudConfig

if typing.TYPE_CHECKING:
    from ...resource.file import FileResource
    from ...resource.service import ServiceResourceBase


@dataclasses.dataclass
class ContainerModelBuildArgs:
    opts: ResourceOptions | None = None
    envs: Mapping[str, Input[str]] = dataclasses.field(default_factory=dict)
    volumes: Mapping[str, ContainerVolumeConfig] = dataclasses.field(
        default_factory=dict
    )
    files: Sequence[FileResource] = dataclasses.field(default_factory=list)
    aliases: dict[str, list[str]] = dataclasses.field(default_factory=dict)


class ContainerModel(HomelabBaseModel):
    active: bool = True
    inherit: ContainerInheritConfig = ContainerInheritConfig()

    raw_image: ContainerImageModelConfig | None = Field(None, alias="image")

    capabilities: list[str] | None = None
    command: list[GlobalExtract] | None = None
    databases: list[ContainerDatabaseConfig] | None = None
    devices: list[AbsolutePath] | None = None
    docker_socket: ContainerDockerSocketConfig | None = None
    entrypoint: list[GlobalExtract] | None = None
    group_adds: list[str] | None = None
    healthcheck: ContainerHealthCheckConfig | None = None
    hostname: GlobalExtract | None = None
    hosts: list[ContainerHostConfig] = []
    init: bool | None = None
    mails: list[ContainerMailConfig] | None = None
    network: ContainerNetworkConfig = ContainerNetworkConfig()
    ports: dict[str, ContainerPortsConfig | ContainerPortConfig] = {}
    privileged: bool | None = None
    read_only: bool = True
    remove: bool = False
    restart: Literal["unless-stopped"] = "unless-stopped"
    sysctls: dict[str, str] | None = None
    tmpfs: list[ContainerTmpfsConfig] | None = None
    user: str | None = None
    volumes: ContainerVolumesConfig = ContainerVolumesConfig()
    wait: bool = True
    wait_timeout: PositiveInt | None = None
    wud: ContainerWudConfig | None = None

    envs: dict[str, GlobalExtract] = {}
    labels: dict[str, GlobalExtract] = {}

    @property
    def image(self) -> ContainerImageModelConfig:
        if not self.raw_image:
            raise ValueError("Image config model is None")
        return self.raw_image

    def model(self, main_service: ServiceResourceBase) -> ContainerModel:
        if "inherit" in self.model_fields_set:
            inherit = self.inherit.to_full()
            service = (
                main_service
                if inherit.service is None
                else main_service.SERVICES[inherit.service]
            )
            return service.model[inherit.container].model_merge(self, override=True)
        return self

    def build_command(
        self, main_service: ServiceResourceBase
    ) -> list[Output[str]] | None:
        return (
            [
                GlobalExtractor(command).extract_str(main_service, self)
                for command in self.command
            ]
            if self.command is not None
            else None
        )

    def build_entrypoint(
        self, main_service: ServiceResourceBase
    ) -> list[Output[str]] | None:
        return (
            [
                GlobalExtractor(entrypoint).extract_str(main_service, self)
                for entrypoint in self.entrypoint
            ]
            if self.entrypoint is not None
            else None
        )

    def build_ports(self) -> dict[str, ContainerPortConfig]:
        results: dict[str, ContainerPortConfig] = {}
        for key, config in self.ports.items():
            if isinstance(config, ContainerPortConfig):
                results[key] = config
            else:
                for port in config.to_ports():
                    results["{}-{}-{}".format(key, port.internal, port.ip)] = port
        return results

    def build_tmpfs(self) -> dict[str, str] | None:
        return (
            {
                tmpfs[0].as_posix(): tmpfs[1]
                for tmpfs in [tmpfs.to_args() for tmpfs in self.tmpfs]
            }
            if self.tmpfs
            else None
        )

    def build_envs(
        self,
        main_service: ServiceResourceBase,
        build_args: ContainerModelBuildArgs,
    ) -> list[Output[str]]:
        additional_envs: dict[str, Output[str]] = {}
        if self.databases:
            for database in self.databases:
                additional_envs |= database.build_envs(main_service.database)
        if self.mails:
            for mail in self.mails:
                additional_envs |= mail.to_envs(main_service)

        return [
            Output.concat(k, "=", v)
            for k, v in sorted(
                (
                    {
                        "TZ": Output.from_input(
                            main_service.docker_resource_args.timezone
                        )
                    }
                    | {
                        k: Output.from_input(
                            GlobalExtractor(v).extract_str(main_service, self)
                        )
                        for k, v in self.envs.items()
                    }
                    | {
                        k: Output.from_input(v)
                        for k, v in (dict(build_args.envs) | additional_envs).items()
                    }
                ).items(),
                key=lambda x: x[0],
            )
        ]

    def build_labels(
        self,
        resource_name: str | None,
        main_service: ServiceResourceBase,
        build_args: ContainerModelBuildArgs,
    ) -> dict[Output[str], Output[str]]:
        return (
            {
                Output.from_input(k): Output.from_input(v)
                for k, v in (
                    main_service.docker_resource_args.project_labels
                    | {"dev.dozzle.group": main_service.name()}
                    | ({"dev.dozzle.name": resource_name} if resource_name else {})
                    | (self.wud.build_labels(resource_name) if self.wud else {})
                ).items()
            }
            | {
                Output.from_input(k): GlobalExtractor(v).extract_str(main_service, self)
                for k, v in self.labels.items()
            }
            | {file.id: file.hash for file in build_args.files}
        )

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        build_args: ContainerModelBuildArgs | None,
    ) -> docker.Container:
        docker_resource_args = main_service.docker_resource_args
        model = self.model(main_service)

        build_args = build_args or ContainerModelBuildArgs()
        network_args = model.network.to_args(resource_name, main_service, build_args)

        depends_on: list[Resource] = []
        depends_on.extend(build_args.files)
        if model.databases:
            depends_on.extend(
                database.to_container(main_service.database)
                for database in model.databases
            )

        return docker.Container(
            resource_name,
            opts=ResourceOptions.merge(
                ResourceOptions.merge(opts, build_args.opts),
                ResourceOptions(replace_on_changes=["*"], depends_on=depends_on),
            ),
            image=model.image.to_image_name(docker_resource_args.image),
            capabilities=docker.ContainerCapabilitiesArgs(adds=model.capabilities)
            if model.capabilities
            else None,
            command=model.build_command(main_service),
            devices=[
                docker.ContainerDeviceArgs(
                    host_path=device.as_posix(), container_path=device.as_posix()
                )
                for device in model.devices
            ]
            if model.devices
            else None,
            group_adds=model.group_adds,
            entrypoints=model.build_entrypoint(main_service),
            healthcheck=model.healthcheck.to_args(main_service, model)
            if model.healthcheck
            else None,
            hostname=GlobalExtractor(model.hostname).extract_str(main_service, model)
            if model.hostname
            else None,
            hosts=[host.to_args() for host in model.hosts] if model.hosts else None,
            init=model.init,
            network_mode=network_args.mode,
            networks_advanced=network_args.advanced,
            ports=[port.to_args() for port in sorted(model.build_ports().values())],
            privileged=model.privileged,
            read_only=model.read_only,
            rm=model.remove,
            restart=model.restart,
            sysctls=model.sysctls,
            tmpfs=model.build_tmpfs(),
            user=model.user,
            volumes=model.volumes.to_args(
                model.docker_socket, main_service, model, build_args
            ),
            wait=model.wait if model.healthcheck else False,
            wait_timeout=model.wait_timeout,
            envs=model.build_envs(main_service, build_args),
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in (
                    model.build_labels(resource_name, main_service, build_args)
                    | {
                        "pulumi.image.id": model.image.to_image_id(
                            docker_resource_args.image
                        )
                    }
                ).items()
            ],
        )
