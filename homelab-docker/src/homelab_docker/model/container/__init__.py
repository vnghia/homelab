from typing import Literal

import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel

from homelab_docker.model.container.healthcheck import Healthcheck
from homelab_docker.model.container.network import Network
from homelab_docker.model.container.port import Port
from homelab_docker.model.container.volume import Volume
from homelab_docker.resource import GlobalResource


class Container(BaseModel):
    image: str

    capabilities: list[str] | None = None
    healthcheck: Healthcheck | None = None
    network: Network = Network()
    ports: dict[str, Port] = {}
    read_only: bool = True
    remove: bool = False
    restart: Literal["unless-stopped"] = "unless-stopped"
    sysctls: dict[str, str] | None = None
    volumes: dict[str, Volume] = {}
    wait: bool = True

    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        global_: GlobalResource,
        containers: dict[str, docker.Container],
        project_labels: dict[str, str],
    ) -> docker.Container:
        image = global_.image[self.image]
        network_args = self.network.to_args(global_, containers)

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
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in (
                    project_labels
                    | self.labels
                    | {"image.repo_digest": image.repo_digest}
                ).items()
            ],
        )
