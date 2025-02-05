from typing import Literal

import pulumi_docker as docker
from pulumi import Input, Output, ResourceOptions
from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from homelab_docker.file import File
from homelab_docker.interpolation.container_string import ContainerString
from homelab_docker.resource.global_ import Global as GlobalResource

from .healthcheck import Healthcheck
from .network import Network
from .port import Port
from .volume import Volumes


class Model(BaseModel):
    image: str

    capabilities: list[str] | None = None
    command: list[ContainerString] | None = None
    healthcheck: Healthcheck | None = None
    network: Network = Network()
    ports: dict[str, Port] = {}
    read_only: bool = True
    remove: bool = False
    restart: Literal["unless-stopped"] = "unless-stopped"
    sysctls: dict[str, str] | None = None
    volumes: Volumes = Volumes()
    wait: bool = True

    envs: dict[str, ContainerString] = {}
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        timezone: TimeZoneName,
        global_resource: GlobalResource,
        containers: dict[str, docker.Container],
        envs: dict[str, Input[str]] | None,
        files: list[File] | None,
        project_labels: dict[str, str],
    ) -> docker.Container:
        image = global_resource.image[self.image]
        network_args = self.network.to_args(global_resource.network, containers)

        return docker.Container(
            resource_name,
            opts=ResourceOptions.merge(
                opts,
                ResourceOptions(
                    ignore_changes=["image"], replace_on_changes=["*"], depends_on=files
                ),
            ),
            image=image.name,
            capabilities=docker.ContainerCapabilitiesArgs(adds=self.capabilities)
            if self.capabilities
            else None,
            command=[
                command.to_str(container_volumes=self.volumes)
                for command in self.command
            ]
            if self.command
            else None,
            healthcheck=self.healthcheck.to_args() if self.healthcheck else None,
            network_mode=network_args.mode,
            networks_advanced=network_args.advanced,
            ports=[port.to_args() for port in sorted(self.ports.values())],
            read_only=self.read_only,
            rm=self.remove,
            restart=self.restart,
            sysctls=self.sysctls,
            volumes=self.volumes.to_args(volume_resource=global_resource.volume),
            wait=self.wait if self.healthcheck else False,
            envs=[
                Output.concat(
                    k,
                    "=",
                    Output.from_input(v).apply(
                        lambda x: x.to_str(container_volumes=self.volumes)
                        if isinstance(x, ContainerString)
                        else x
                    ),
                )
                for k, v in sorted(
                    (
                        {"TZ": Output.from_input(ContainerString(timezone))}
                        | self.envs
                        | {
                            k: Output.from_input(v).apply(ContainerString)
                            for k, v in (envs or {}).items()
                        }
                    ).items(),
                    key=lambda x: x[0],
                )
            ],
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in (
                    project_labels
                    | self.labels
                    | {"image.repo_digest": image.repo_digest}
                ).items()
            ],
        )
