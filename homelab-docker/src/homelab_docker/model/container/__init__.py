from __future__ import annotations

import dataclasses
import typing
from typing import Literal, Mapping, Sequence

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pulumi import Input, Output, Resource, ResourceOptions

from .database import ContainerDatabaseConfig
from .docker_socket import ContainerDockerSocketConfig
from .extract import ContainerExtract
from .healthcheck import ContainerHealthCheckConfig
from .image import ContainerImageModelConfig
from .network import ContainerNetworkConfig
from .port import ContainerPortConfig
from .tmpfs import ContainerTmpfsConfig
from .volume import ContainerVolumeConfig, ContainerVolumesConfig

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
    files: Sequence["FileResource"] = dataclasses.field(default_factory=list)


class ContainerModel(HomelabBaseModel):
    active: bool = True
    image: ContainerImageModelConfig

    capabilities: list[str] | None = None
    command: list[ContainerExtract] | None = None
    database: ContainerDatabaseConfig | None = None
    docker_socket: ContainerDockerSocketConfig | None = None
    entrypoint: list[ContainerExtract] | None = None
    healthcheck: ContainerHealthCheckConfig | None = None
    init: bool | None = None
    network: ContainerNetworkConfig = ContainerNetworkConfig()
    ports: dict[str, ContainerPortConfig] = {}
    read_only: bool = True
    remove: bool = False
    restart: Literal["unless-stopped"] = "unless-stopped"
    sysctls: dict[str, str] | None = None
    tmpfs: list[ContainerTmpfsConfig] | None = None
    user: str | None = None
    volumes: ContainerVolumesConfig = ContainerVolumesConfig()
    wait: bool = True

    envs: dict[str, ContainerExtract] = {}
    labels: dict[str, str] = {}

    def build_command(self) -> list[str] | None:
        return (
            [command.extract_str(self) for command in self.command]
            if self.command is not None
            else None
        )

    def build_entrypoint(self) -> list[str] | None:
        return (
            [entrypoint.extract_str(self) for entrypoint in self.entrypoint]
            if self.entrypoint is not None
            else None
        )

    def build_tmpfs(self) -> list[docker.ContainerMountArgs] | None:
        return [tmpfs.to_args() for tmpfs in self.tmpfs] if self.tmpfs else None

    def build_envs(
        self,
        main_service: ServiceResourceBase,
        build_args: ContainerModelBuildArgs,
    ) -> list[Output[str]]:
        database_envs: dict[str, Output[str]] = {}

        if self.database:
            if not main_service.database:
                raise ValueError("Database is required if database config is not None")
            database_envs = self.database.build_envs(main_service.database)

        return [
            Output.concat(k, "=", v)
            for k, v in sorted(
                (
                    {
                        "TZ": Output.from_input(
                            str(main_service.docker_resource_args.timezone)
                        )
                    }
                    | {
                        k: Output.from_input(v.extract_str(self))
                        for k, v in self.envs.items()
                    }
                    | {
                        k: Output.from_input(v)
                        for k, v in (dict(build_args.envs) | database_envs).items()
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
        return {
            Output.from_input(k): Output.from_input(v)
            for k, v in (
                main_service.docker_resource_args.project_labels
                | self.labels
                | {"dev.dozzle.group": main_service.name()}
                | ({"dev.dozzle.name": resource_name} if resource_name else {})
            ).items()
        } | {file.id: file.hash for file in build_args.files}

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        build_args: ContainerModelBuildArgs | None,
    ) -> docker.Container:
        docker_resource_args = main_service.docker_resource_args

        build_args = build_args or ContainerModelBuildArgs()
        network_args = self.network.to_args(resource_name, main_service)

        depends_on: list[Resource] = []
        depends_on.extend(build_args.files)

        if self.database:
            if not main_service.database:
                raise ValueError("Database is required if database config is not None")
            depends_on.append(self.database.to_container(main_service.database))

        return docker.Container(
            resource_name,
            opts=ResourceOptions.merge(
                ResourceOptions.merge(opts, build_args.opts),
                ResourceOptions(
                    ignore_changes=["image"],
                    replace_on_changes=["*"],
                    depends_on=depends_on,
                ),
            ),
            image=self.image.to_image_name(docker_resource_args.image),
            capabilities=docker.ContainerCapabilitiesArgs(adds=self.capabilities)
            if self.capabilities
            else None,
            command=self.build_command(),
            entrypoints=self.build_entrypoint(),
            healthcheck=self.healthcheck.to_args(self) if self.healthcheck else None,
            init=self.init,
            mounts=self.build_tmpfs(),
            network_mode=network_args.mode,
            networks_advanced=network_args.advanced,
            ports=[port.to_args() for port in sorted(self.ports.values())],
            read_only=self.read_only,
            rm=self.remove,
            restart=self.restart,
            sysctls=self.sysctls,
            user=self.user,
            volumes=self.volumes.to_args(self.docker_socket, main_service, build_args),
            wait=self.wait if self.healthcheck else False,
            envs=self.build_envs(main_service, build_args),
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in (
                    self.build_labels(resource_name, main_service, build_args)
                    | {
                        "pulumi.image.id": self.image.to_image_id(
                            docker_resource_args.image
                        )
                    }
                ).items()
            ],
        )
