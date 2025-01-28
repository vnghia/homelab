import dataclasses

import pulumi
import pulumi_docker as docker
from homelab_docker.container import Container
from pulumi import ComponentResource, Input, Output, ResourceOptions

from homelab import config
from homelab.docker.image import Image
from homelab.docker.network import Network
from homelab.docker.volume import Volume


@dataclasses.dataclass
class BuildOption:
    opts: ResourceOptions | None = None
    envs: dict[str, Input[str]] = dataclasses.field(default_factory=dict)


class Base(ComponentResource):
    def __init__(
        self,
        network: Network,
        image: Image,
        volume: Volume,
        resource_name: str,
        opts: ResourceOptions | None,
    ) -> None:
        self.network = network
        self.image = image
        self.volume = volume
        self.resource_name = resource_name
        super().__init__(resource_name, resource_name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

    def build_container(
        self, name: str, model: Container, option: BuildOption | None = None
    ) -> docker.Container:
        option = option or BuildOption()
        return model.build_resource(
            name,
            networks=self.network.networks,
            images=self.image.remotes,
            volumes=self.volume.volumes,
            opts=ResourceOptions.merge(self.child_opts, option.opts),
            envs=option.envs,
        )

    def build_containers(
        self, options: dict[str, BuildOption] = {}
    ) -> dict[str, docker.Container]:
        self.containers = {
            name: self.build_container(name, model, options.get(name))
            for name, model in config.docker.services[
                self.resource_name
            ].containers.items()
        }
        self.container = self.containers[self.resource_name]
        for name, container in self.containers.items():
            pulumi.export(f"container-{name}", container.name)

        return self.containers

    def container_outputs(self) -> dict[str, Output[str]]:
        return {name: container.name for name, container in self.containers.items()}
