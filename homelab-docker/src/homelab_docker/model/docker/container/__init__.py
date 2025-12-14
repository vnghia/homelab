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

from ....extract.global_ import GlobalExtractor
from .cap import ContainerCapConfig
from .database import ContainerDatabaseConfig
from .docker_socket import ContainerDockerSocketConfig
from .healthcheck import ContainerHealthCheckConfig
from .host import ContainerHostConfig
from .image import ContainerImageModelConfig
from .inherit import ContainerInheritConfig
from .mail import ContainerMailConfig
from .network import (
    ContainerBridgeNetworkConfig,
    ContainerCommonNetworkConfig,
    ContainerNetworkConfig,
)
from .ports import ContainerPortsConfig
from .tmpfs import ContainerTmpfsConfig
from .user import ContainerUserConfig
from .volume import ContainerVolumeConfig, ContainerVolumesConfig
from .wud import ContainerWudConfig

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs
    from ....resource.file import FileResource


@dataclasses.dataclass
class ContainerNetworkModelBuildArgs:
    hosts: list[ContainerHostConfig] = dataclasses.field(default_factory=list)
    ports: ContainerPortsConfig = dataclasses.field(
        default_factory=ContainerPortsConfig
    )
    bridges: dict[str, ContainerBridgeNetworkConfig] = dataclasses.field(
        default_factory=dict
    )

    def __iadd__(
        self, rhs: ContainerNetworkModelBuildArgs
    ) -> ContainerNetworkModelBuildArgs:
        self.add_hosts(rhs.hosts)
        self.add_ports(rhs.ports)
        self.add_bridges(rhs.bridges)
        return self

    def add_hosts(self, hosts: list[ContainerHostConfig]) -> None:
        self.hosts += hosts

    def add_ports(self, ports: ContainerPortsConfig) -> None:
        self.ports |= ports

    def add_bridges(self, bridges: dict[str, ContainerBridgeNetworkConfig]) -> None:
        self.bridges |= bridges


@dataclasses.dataclass
class ContainerModelBuildArgs:
    opts: ResourceOptions | None = None
    envs: Mapping[str, Input[str]] = dataclasses.field(default_factory=dict)
    volumes: Mapping[str, ContainerVolumeConfig] = dataclasses.field(
        default_factory=dict
    )
    files: Sequence[FileResource] = dataclasses.field(default_factory=list)

    network: ContainerNetworkModelBuildArgs = dataclasses.field(
        default_factory=ContainerNetworkModelBuildArgs
    )

    def add_envs(self, envs: Mapping[str, Input[str]]) -> None:
        self.envs = {**self.envs, **envs}

    def add_volumes(self, volumes: Mapping[str, ContainerVolumeConfig]) -> None:
        self.volumes = {**self.volumes, **volumes}

    def add_files(self, files: Sequence[FileResource]) -> None:
        self.files = [*self.files, *files]

    def add_network(self, network: ContainerNetworkModelBuildArgs) -> None:
        self.network += network


class ContainerModel(HomelabBaseModel):
    active: bool = True
    experimental: bool = False
    delete_before_replace: bool = False
    inherit: ContainerInheritConfig = ContainerInheritConfig()

    raw_image: ContainerImageModelConfig | None = Field(None, alias="image")

    cap: ContainerCapConfig = ContainerCapConfig()
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
    ports: ContainerPortsConfig = ContainerPortsConfig()
    privileged: bool | None = None
    read_only: bool = True
    remove: bool = False
    restart: Literal["unless-stopped"] = "unless-stopped"
    security_opts: list[str] = ["no-new-privileges"]
    sysctls: dict[str, str] | None = None
    tmpfs: list[ContainerTmpfsConfig] | None = None
    user: ContainerUserConfig = ContainerUserConfig()
    volumes: ContainerVolumesConfig = ContainerVolumesConfig()
    wait: bool = True
    wait_timeout: PositiveInt | None = None
    wud: ContainerWudConfig | None = None

    envs: dict[str, GlobalExtract | None] = {}
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
                else extractor_args.host_model.services[inherit.service]
            )
            return models[inherit.container].model_merge(self, override=True)
        return self

    def build_cap(self) -> docker.ContainerCapabilitiesArgs | None:
        if self.experimental and self.cap:
            return docker.ContainerCapabilitiesArgs(
                adds=self.cap.add, drops=self.cap.drop
            )
        return None

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

    def build_tmpfs(self) -> dict[str, str] | None:
        return (
            {
                tmpfs[0].as_posix(): tmpfs[1]
                for tmpfs in [tmpfs.to_args() for tmpfs in self.tmpfs]
            }
            if self.tmpfs
            else None
        )

    def build_user(self) -> str | None:
        if (self.experimental and not self.user.is_root) or (
            not self.experimental and not self.user.is_default
        ):
            return self.user.user
        return None

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
                    {"TZ": Output.from_input(extractor_args.host_model.timezone)}
                    | {
                        k: Output.from_input(
                            GlobalExtractor(v).extract_str(extractor_args)
                        )
                        for k, v in self.envs.items()
                        if v is not None
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
                    extractor_args.global_resource.project_args.labels
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

    def build_hosts(
        self, extractor_args: ExtractorArgs, build_args: ContainerModelBuildArgs
    ) -> list[docker.ContainerHostArgs] | None:
        network = self.network.root
        if isinstance(network, ContainerCommonNetworkConfig):
            hosts = self.hosts + build_args.network.hosts
            return [host.to_args(extractor_args) for host in hosts] if hosts else None
        return None

    def build_ports(
        self, extractor_args: ExtractorArgs, build_args: ContainerModelBuildArgs
    ) -> Output[list[docker.ContainerPortArgs]]:
        network = self.network.root
        if isinstance(network, ContainerCommonNetworkConfig):
            return self.ports.to_args(extractor_args, build_args)
        return Output.from_input([])

    def build_args(
        self,
        build_args: ContainerModelBuildArgs | None,
        extractor_args: ExtractorArgs,
    ) -> ContainerModelBuildArgs:
        build_args = build_args or ContainerModelBuildArgs()
        files = list(build_args.files)
        for volume in self.volumes.volumes:
            if isinstance(volume, str):
                files += extractor_args.host.docker.volume.files[volume]
        build_args.files = files
        return build_args

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

        build_args = self.build_args(build_args, extractor_args)
        network_args = self.network.to_args(resource_name, extractor_args, build_args)

        depends_on: list[Resource] = []
        depends_on.extend(build_args.files)
        if self.databases:
            depends_on.extend(
                service.containers[
                    database.to_container_name(service.database)
                ].resource
                for database in self.databases
            )

        resource_labels = {}
        if (
            digest := self.image.to_build_image_digest(extractor_args.host.docker.image)
        ) is not None:
            resource_labels["image.build.digest"] = digest

        return docker.Container(
            resource_name,
            opts=ResourceOptions.merge(
                opts,
                ResourceOptions.merge(
                    build_args.opts,
                    ResourceOptions(
                        depends_on=depends_on,
                        delete_before_replace=self.delete_before_replace
                        or bool(self.ports)
                        or bool(build_args.network.ports),
                    ),
                ),
            ),
            image=self.image.to_image_name(extractor_args.host.docker.image),
            capabilities=self.build_cap(),
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
            hosts=self.build_hosts(extractor_args, build_args),
            init=self.init,
            mounts=self.volumes.to_args(self.docker_socket, extractor_args, build_args),
            network_mode=network_args.mode,
            networks_advanced=network_args.advanced,
            ports=self.build_ports(extractor_args, build_args),
            privileged=self.privileged,
            read_only=self.read_only,
            rm=self.remove,
            restart=self.restart,
            security_opts=self.security_opts,
            sysctls=self.sysctls,
            tmpfs=self.build_tmpfs(),
            user=self.build_user(),
            wait=self.wait if self.healthcheck else False,
            wait_timeout=self.wait_timeout,
            envs=self.build_envs(extractor_args, build_args),
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in (
                    self.build_labels(resource_name, extractor_args, build_args)
                    | resource_labels
                ).items()
            ],
        )
