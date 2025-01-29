import dataclasses

import pulumi
import pulumi_docker as docker
from homelab_docker.container import Container
from pulumi import ComponentResource, Input, Output, ResourceOptions

from homelab import config
from homelab.config.docker.service import Service
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
        opts: ResourceOptions | None,
    ) -> None:
        self.network = network
        self.image = image
        self.volume = volume

        super().__init__(self.name(), self.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def config(cls) -> Service:
        return config.docker.services[cls.name()]

    def add_service_name(self, name: str | None) -> str:
        return f"{self.name()}-{name}" if name else self.name()

    def build_container(
        self, name: str | None, model: Container, option: BuildOption | None = None
    ) -> docker.Container:
        option = option or BuildOption()
        return model.build_resource(
            self.add_service_name(name),
            timezone=config.docker.timezone,
            networks=self.network.networks,
            images=self.image.remotes,
            volumes=self.volume.volumes,
            opts=ResourceOptions.merge(self.child_opts, option.opts),
            envs=option.envs,
        )

    def build_containers(self, options: dict[str | None, BuildOption] = {}):
        self.container = self.build_container(
            None, self.config().container, options.get(None)
        )
        self.containers = {
            name: self.build_container(name, model, options.get(name))
            for name, model in self.config().containers.items()
        } | {None: self.container}

        for name, container in self.containers.items():
            pulumi.export(f"container-{self.add_service_name(name)}", container.name)

    def container_outputs(self) -> dict[str, Output[str]]:
        return {
            name or self.name(): container.name
            for name, container in self.containers.items()
        }
