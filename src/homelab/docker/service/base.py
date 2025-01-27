import pulumi
import pulumi_docker as docker
from pulumi import ComponentResource, Input, Output, ResourceOptions

from homelab import config
from homelab.docker.image import Image
from homelab.docker.network import Network
from homelab.docker.volume import Volume


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

    def build_containers(
        self, envs: dict[str, dict[str, Input[str]]] = {}
    ) -> dict[str, docker.Container]:
        self.containers = {
            name: model.build_resource(
                self.resource_name,
                networks=self.network.networks,
                images=self.image.remotes,
                volumes=self.volume.volumes,
                opts=self.child_opts,
                envs=envs.get(name, {}),
            )
            for name, model in config.docker.services[
                self.resource_name
            ].containers.items()
        }

        for name, container in self.containers.items():
            pulumi.export(f"container-{name}", container.name)

        return self.containers

    def container_outputs(self) -> dict[str, Output[str]]:
        return {name: container.name for name, container in self.containers.items()}
