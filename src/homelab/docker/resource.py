import pulumi_docker as docker
from homelab_docker.container.resource import Resource as DockerResource
from pulumi import ResourceOptions

from homelab.docker.image import Image
from homelab.docker.network import Network
from homelab.docker.volume import Volume


class Resource:
    def __init__(self, opts: ResourceOptions | None = None) -> None:
        self.network = Network(opts=opts)
        self.image = Image(opts=opts)
        self.volume = Volume(opts=opts)
        self.containers: dict[str, docker.Container] = {}

    @property
    def networks(self) -> dict[str, docker.Network]:
        return self.network.networks

    @property
    def images(self) -> dict[str, docker.RemoteImage]:
        return self.image.remotes

    @property
    def volumes(self) -> dict[str, docker.Volume]:
        return self.volume.volumes

    def to_docker_resource(self) -> DockerResource:
        return DockerResource(
            networks=self.networks,
            images=self.images,
            volumes=self.volumes,
            containers=self.containers,
        )
