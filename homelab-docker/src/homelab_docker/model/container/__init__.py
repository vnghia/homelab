from typing import Literal

import pulumi_docker as docker
from pulumi import Input, Output, ResourceOptions
from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from homelab_docker.interpolation.container_string import ContainerString
from homelab_docker.model.container.healthcheck import Healthcheck
from homelab_docker.model.container.network import Network
from homelab_docker.model.container.port import Port
from homelab_docker.model.container.volume import Volume
from homelab_docker.resource.global_ import Global as GlobalResource


class Container(BaseModel):
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
    volumes: dict[str, Volume] = {}
    wait: bool = True

    envs: dict[str, ContainerString] = {}
    labels: dict[str, str] = {}

    def build_resource[T](
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        timezone: TimeZoneName,
        global_: GlobalResource[T],
        containers: dict[str, docker.Container],
        envs: dict[str, Input[str]] = {},
        project_labels: dict[str, str],
    ) -> docker.Container:
        image = global_.image[self.image]
        network_args = self.network.to_args(global_.network, containers)

        return docker.Container(
            resource_name,
            opts=ResourceOptions.merge(
                opts,
                ResourceOptions(
                    ignore_changes=["image"],
                    replace_on_changes=["*"],
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
            volumes=[
                volume.to_args(volume_name=global_.volume[name].name)
                for name, volume in self.volumes.items()
            ]
            + [
                docker.ContainerVolumeArgs(
                    container_path="/etc/localtime",
                    host_path="/etc/localtime",
                    read_only=True,
                ),
                docker.ContainerVolumeArgs(
                    container_path="/usr/share/zoneinfo",
                    host_path="/usr/share/zoneinfo",
                    read_only=True,
                ),
            ],
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
                        {"TZ": Output.from_input(ContainerString(data=timezone))}
                        | self.envs
                        | {
                            k: Output.from_input(v).apply(
                                lambda x: ContainerString(data=x)
                            )
                            for k, v in envs.items()
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
