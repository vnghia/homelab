import deepmerge
import pulumi_docker as docker
from pulumi import Input, Output, ResourceOptions
from pydantic import BaseModel, ConfigDict

from homelab_docker.container.env import Env
from homelab_docker.container.healthcheck import Healthcheck
from homelab_docker.container.network import Network
from homelab_docker.container.port import Port
from homelab_docker.container.tmpfs import Tmpfs
from homelab_docker.container.volume import Volume


class Container(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str | None = None
    capabilities: list[str] | None = None
    healthcheck: Healthcheck | None = None
    ports: dict[str, Port] = {}
    restart: str = "unless-stopped"
    read_only: bool = True
    remove: bool = False
    sysctls: dict[str, str] | None = None
    tmpfs: list[Tmpfs] = []
    wait: bool = True

    image: str

    docker_sock_ro: bool | None = None
    networks: dict[str, Network] = {}
    volumes: dict[str, Volume] = {}
    envs: dict[str, Env] = {}
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        networks: dict[str, docker.Network],
        images: dict[str, docker.RemoteImage],
        volumes: dict[str, docker.Volume],
        opts: ResourceOptions | None = None,
        envs: dict[str, Input[str]] = {},
    ) -> docker.Container:
        image = images[self.image]
        return docker.Container(
            resource_name,
            opts=ResourceOptions.merge(opts, ResourceOptions(ignore_changes=["image"])),
            image=image.name,
            name=self.name,
            capabilities=docker.ContainerCapabilitiesArgs(adds=self.capabilities)
            if self.capabilities
            else None,
            healthcheck=self.healthcheck.to_container_healthcheck()
            if self.healthcheck
            else None,
            ports=[
                port.to_container_port()
                for port in sorted(self.ports.values(), key=lambda x: x.to_comparable())
            ],
            read_only=self.read_only,
            restart=self.restart,
            rm=self.remove,
            sysctls=self.sysctls,
            wait=self.wait,
            mounts=[tmpfs.to_container_mount() for tmpfs in self.tmpfs],
            # TODO: remove this line after https://github.com/pulumi/pulumi-docker/issues/1272
            network_mode="bridge",
            networks_advanced=[
                v.to_container_network_advance(resource_name, networks[k])
                for k, v in self.networks.items()
            ],
            volumes=[
                v.to_container_volume(name=volumes[k].name)
                for k, v in self.volumes.items()
            ]
            + (
                [
                    docker.ContainerVolumeArgs(
                        container_path="/var/run/docker.sock",
                        host_path="/var/run/docker.sock",
                        read_only=self.docker_sock_ro,
                    )
                ]
                if self.docker_sock_ro is not None
                else []
            ),
            envs=[
                Output.concat(
                    k,
                    "=",
                    Output.from_input(v).apply(
                        lambda x: x.to_str(self.volumes) if isinstance(x, Env) else x
                    ),
                )
                for k, v in deepmerge.always_merger.merge(self.envs, envs).items()  # type: ignore[attr-defined]
            ],
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in self.labels.items()
            ]
            + [docker.ContainerLabelArgs(label="image.id", value=image.image_id)],
        )
