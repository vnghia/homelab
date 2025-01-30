import deepmerge
import pulumi_docker as docker
from pulumi import Input, Output, ResourceOptions
from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator
from pydantic_extra_types.timezone_name import TimeZoneName

from homelab_docker.container.healthcheck import Healthcheck
from homelab_docker.container.network import Network
from homelab_docker.container.port import Port
from homelab_docker.container.resource import Resource
from homelab_docker.container.string import String
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
    command: list[String] | None = None
    network_mode: str | None = None
    networks: dict[str, Network] | None = None
    volumes: dict[str, Volume] = {}
    envs: dict[str, String] = {}
    labels: dict[str, str] = {}

    @field_validator("networks", mode="after")
    def network_exclusive(
        cls, networks: dict[str, Network] | None, info: ValidationInfo
    ) -> dict[str, Network] | None:
        if info.data["network_mode"] is not None and networks is not None:
            raise ValueError(
                "`network_mode` and `networks` fields are mutually exclusive"
            )
        return networks

    def build_resource(
        self,
        resource_name: str,
        timezone: TimeZoneName,
        resource: Resource,
        opts: ResourceOptions | None = None,
        envs: dict[str, Input[str]] = {},
    ) -> docker.Container:
        image = resource.images[self.image]
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
            wait=self.wait if self.healthcheck else False,
            command=[command.to_str(volumes=self.volumes) for command in self.command]
            if self.command
            else None,
            mounts=[tmpfs.to_container_mount() for tmpfs in self.tmpfs],
            # TODO: remove this line after https://github.com/pulumi/pulumi-docker/issues/1272
            network_mode=resource.containers[self.network_mode].id.apply(
                lambda x: f"container:{x}"
            )
            if self.network_mode
            else "bridge",
            networks_advanced=[
                v.to_container_network_advance(resource_name, resource.networks[k])
                for k, v in self.networks.items()
            ]
            if self.networks
            else None,
            volumes=[
                v.to_container_volume(name=resource.volumes[k].name)
                for k, v in self.volumes.items()
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
                        lambda x: x.to_str(volumes=self.volumes)
                        if isinstance(x, String)
                        else x
                    ),
                )
                for k, v in sorted(
                    deepmerge.always_merger.merge(
                        self.envs, envs | {"TZ": timezone}
                    ).items(),  # type: ignore[attr-defined]
                    key=lambda x: x[0],
                )
            ],
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in self.labels.items()
            ]
            + [docker.ContainerLabelArgs(label="image.id", value=image.image_id)],
        )
