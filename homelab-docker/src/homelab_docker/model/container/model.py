import dataclasses
from typing import Literal, Mapping

import pulumi_docker as docker
from pulumi import Input, Output, ResourceOptions
from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from homelab_docker.resource.docker import DockerResource
from homelab_docker.resource.file import FileResource

from .healthcheck import ContainerHealthCheckConfig
from .network import ContainerCommonNetworkConfig, ContainerNetworkConfig
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
class ContainerModelBuildArgs:
    opts: ResourceOptions | None = None
    envs: Mapping[str, Input[str]] = dataclasses.field(default_factory=dict)
    files: list[FileResource] = dataclasses.field(default_factory=list)


class ContainerModel(BaseModel):
    image: str

    capabilities: list[str] | None = None
    command: list[ContainerString] | None = None
    healthcheck: ContainerHealthCheckConfig | None = None
    network: ContainerNetworkConfig = ContainerNetworkConfig(
        ContainerCommonNetworkConfig()  # type: ignore [call-arg]
    )
    ports: dict[str, ContainerPortConfig] = {}
    read_only: bool = True
    remove: bool = False
    restart: Literal["unless-stopped"] = "unless-stopped"
    sysctls: dict[str, str] | None = None
    tmpfs: list[ContainerTmpfsConfig] | None = None
    volumes: ContainerVolumesConfig = ContainerVolumesConfig()
    wait: bool = True

    envs: dict[str, ContainerString] = {}
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        global_args: ContainerModelGlobalArgs,
        build_args: ContainerModelBuildArgs | None,
        containers: dict[str, docker.Container],
    ) -> docker.Container:
        build_args = build_args or ContainerModelBuildArgs()
        image = global_args.docker_resource.image[self.image]
        network_args = self.network.to_args(
            global_args.docker_resource.network, containers
        )

        return docker.Container(
            resource_name,
            opts=ResourceOptions.merge(
                ResourceOptions.merge(opts, build_args.opts),
                ResourceOptions(
                    ignore_changes=["image"],
                    replace_on_changes=["*"],
                    depends_on=build_args.files,
                ),
            ),
            image=image.name,
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
                            for k, v in (build_args.envs).items()
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
                    | {"image.repo_digest": image.repo_digest}
                    | {file.id: file.hash for file in build_args.files}
                ).items()
            ],
        )
