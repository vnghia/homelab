import dataclasses
from typing import Literal, Mapping

import pulumi_docker as docker
from pulumi import Input, Output, Resource, ResourceOptions
from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from homelab_docker.config.database import DatabaseConfig
from homelab_docker.config.database.source import DatabaseSourceConfig
from homelab_docker.model.container.database import ContainerDatabaseConfig
from homelab_docker.resource.docker import DockerResource
from homelab_docker.resource.file import FileResource

from .healthcheck import ContainerHealthCheckConfig
from .image import ContainerImageModelConfig
from .network import ContainerNetworkConfig
from .port import ContainerPortConfig
from .string import ContainerString
from .tmpfs import ContainerTmpfsConfig
from .volume import ContainerVolumesConfig


@dataclasses.dataclass
class ContainerModelGlobalArgs:
    timezone: TimeZoneName
    docker_resource: DockerResource
    project_labels: dict[str, str]


@dataclasses.dataclass
class ContainerModelServiceArgs:
    database_config: DatabaseConfig
    database_source_config: DatabaseSourceConfig


@dataclasses.dataclass
class ContainerModelBuildArgs:
    opts: ResourceOptions | None = None
    envs: Mapping[str, Input[str]] = dataclasses.field(default_factory=dict)
    files: list[FileResource] = dataclasses.field(default_factory=list)


class ContainerModel(BaseModel):
    image: ContainerImageModelConfig

    capabilities: list[str] | None = None
    command: list[ContainerString] | None = None
    database: ContainerDatabaseConfig | None = None
    healthcheck: ContainerHealthCheckConfig | None = None
    init: bool | None = None
    network: ContainerNetworkConfig = ContainerNetworkConfig()
    ports: dict[str, ContainerPortConfig] = {}
    read_only: bool = True
    remove: bool = False
    restart: Literal["unless-stopped"] = "unless-stopped"
    sysctls: dict[str, str] | None = None
    tmpfs: list[ContainerTmpfsConfig] | None = None
    volumes: ContainerVolumesConfig = ContainerVolumesConfig.model_construct()
    wait: bool = True

    envs: dict[str, ContainerString] = {}
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        service_name: str,
        global_args: ContainerModelGlobalArgs,
        service_args: ContainerModelServiceArgs | None,
        build_args: ContainerModelBuildArgs | None,
        containers: dict[str, docker.Container],
    ) -> docker.Container:
        build_args = build_args or ContainerModelBuildArgs()
        network_args = self.network.to_args(
            resource_name, global_args.docker_resource.network, containers
        )

        depends_on: list[Resource] = []
        depends_on.extend(build_args.files)

        database_envs: dict[str, Output[str]] = {}

        if self.database:
            if not service_args:
                raise ValueError(
                    "service args is required if database config is not None"
                )

            depends_on.append(
                containers[
                    self.database.to_container_name(
                        service_name, service_args.database_config
                    )
                ]
            )

            database_envs = self.database.build_envs(
                service_args.database_config,
                service_args.database_source_config,
            )

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
            image=self.image.to_image_name(global_args.docker_resource.image),
            capabilities=docker.ContainerCapabilitiesArgs(adds=self.capabilities)
            if self.capabilities
            else None,
            command=[
                command.to_str(container_volumes_config=self.volumes)
                for command in self.command
            ]
            if self.command
            else None,
            healthcheck=self.healthcheck.to_args() if self.healthcheck else None,
            init=self.init,
            mounts=[tmpfs.to_args() for tmpfs in self.tmpfs] if self.tmpfs else None,
            network_mode=network_args.mode,
            networks_advanced=network_args.advanced,
            ports=[port.to_args() for port in sorted(self.ports.values())],
            read_only=self.read_only,
            rm=self.remove,
            restart=self.restart,
            sysctls=self.sysctls,
            volumes=self.volumes.to_args(
                volume_resource=global_args.docker_resource.volume
            ),
            wait=self.wait if self.healthcheck else False,
            envs=[
                Output.concat(
                    k,
                    "=",
                    Output.from_input(v).apply(
                        lambda x: x.to_str(container_volumes_config=self.volumes)
                        if isinstance(x, ContainerString)
                        else x
                    ),
                )
                for k, v in sorted(
                    (
                        {"TZ": Output.from_input(ContainerString(global_args.timezone))}
                        | self.envs
                        | {
                            k: Output.from_input(v).apply(ContainerString)
                            for k, v in (dict(build_args.envs) | database_envs).items()
                        }
                    ).items(),
                    key=lambda x: x[0],
                )
            ],
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in (
                    global_args.project_labels
                    | self.labels
                    | {
                        "pulumi.image.id": self.image.to_image_id(
                            global_args.docker_resource.image
                        ),
                        "dev.dozzle.group": Output.from_input(service_name),
                        "dev.dozzle.name": Output.from_input(resource_name),
                    }
                    | {file.id: file.hash for file in build_args.files}
                ).items()
            ],
        )
