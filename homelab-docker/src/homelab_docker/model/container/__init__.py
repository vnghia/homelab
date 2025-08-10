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
    from ...extract import ExtractorArgs
    from ...resource.file import FileResource


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

    def to_full(self, extractor_args: ExtractorArgs) -> ContainerModel:
        if "inherit" in self.model_fields_set:
            inherit = self.inherit.to_full()
            models = (
                extractor_args.service.model
                if inherit.service is None
                else extractor_args.docker_resource_args.config.services[
                    inherit.service
                ]
            )
            return models[inherit.container].model_merge(self, override=True)
        return self

    def build_command(self, extractor_args: ExtractorArgs) -> list[Output[str]] | None:
        return (
            [
                GlobalExtractor(command).extract_str(extractor_args)
                for command in self.command
            ]
            if self.command is not None
            else None
        )

    def build_entrypoint(
        self, extractor_args: ExtractorArgs
    ) -> list[Output[str]] | None:
        return (
            [
                GlobalExtractor(entrypoint).extract_str(extractor_args)
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
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs,
    ) -> list[Output[str]]:
        service = extractor_args.service

        additional_envs: dict[str, Output[str]] = {}
        if self.databases:
            for database in self.databases:
                additional_envs |= database.build_envs(service.database)
        if self.mails:
            for mail in self.mails:
                additional_envs |= mail.to_envs(extractor_args)

        return [
            Output.concat(k, "=", v)
            for k, v in sorted(
                (
                    {
                        "TZ": Output.from_input(
                            extractor_args.docker_resource_args.timezone
                        )
                    }
                    | {
                        k: Output.from_input(
                            GlobalExtractor(v).extract_str(extractor_args)
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
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs,
    ) -> dict[Output[str], Output[str]]:
        service = extractor_args.service

        return (
            {
                Output.from_input(k): Output.from_input(v)
                for k, v in (
                    extractor_args.global_args.project.labels
                    | {"dev.dozzle.group": service.name()}
                    | ({"dev.dozzle.name": resource_name} if resource_name else {})
                    | (self.wud.build_labels(resource_name) if self.wud else {})
                ).items()
            }
            | {
                Output.from_input(k): GlobalExtractor(v).extract_str(extractor_args)
                for k, v in self.labels.items()
            }
            | {file.id: file.hash for file in build_args.files}
        )

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs | None,
    ) -> docker.Container:
        extractor_args = extractor_args.with_container(self)
        service = extractor_args.service
        docker_resource_args = extractor_args.docker_resource_args

        build_args = build_args or ContainerModelBuildArgs()
        network_args = self.network.to_args(resource_name, extractor_args, build_args)

        depends_on: list[Resource] = []
        depends_on.extend(build_args.files)
        if self.databases:
            depends_on.extend(
                database.to_container(service.database) for database in self.databases
            )

        return docker.Container(
            resource_name,
            opts=ResourceOptions.merge(
                ResourceOptions.merge(opts, build_args.opts),
                ResourceOptions(replace_on_changes=["*"], depends_on=depends_on),
            ),
            image=self.image.to_image_name(docker_resource_args.image),
            capabilities=docker.ContainerCapabilitiesArgs(adds=self.capabilities)
            if self.capabilities
            else None,
            command=self.build_command(extractor_args),
            devices=[
                docker.ContainerDeviceArgs(
                    host_path=device.as_posix(), container_path=device.as_posix()
                )
                for device in self.devices
            ]
            if self.devices
            else None,
            group_adds=self.group_adds,
            entrypoints=self.build_entrypoint(extractor_args),
            healthcheck=self.healthcheck.to_args(extractor_args)
            if self.healthcheck
            else None,
            hostname=GlobalExtractor(self.hostname).extract_str(extractor_args)
            if self.hostname
            else None,
            hosts=[host.to_args() for host in self.hosts] if self.hosts else None,
            init=self.init,
            network_mode=network_args.mode,
            networks_advanced=network_args.advanced,
            ports=[port.to_args() for port in sorted(self.build_ports().values())],
            privileged=self.privileged,
            read_only=self.read_only,
            rm=self.remove,
            restart=self.restart,
            sysctls=self.sysctls,
            tmpfs=self.build_tmpfs(),
            user=self.user,
            volumes=self.volumes.to_args(
                self.docker_socket, extractor_args, build_args
            ),
            wait=self.wait if self.healthcheck else False,
            wait_timeout=self.wait_timeout,
            envs=self.build_envs(extractor_args, build_args),
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in (
                    self.build_labels(resource_name, extractor_args, build_args)
                    | {
                        "pulumi.image.id": self.image.to_image_id(
                            docker_resource_args.image
                        )
                    }
                ).items()
            ],
        )
