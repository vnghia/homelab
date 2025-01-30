import pulumi_docker as docker
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
