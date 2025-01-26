from pulumi import ComponentResource, ResourceOptions

from homelab.docker.image import Image
from homelab.docker.network import Network
from homelab.docker.service import Service
from homelab.docker.volume import Volume


class Docker(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(self) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.network = Network(opts=self.child_opts)
        self.image = Image(opts=self.child_opts)
        self.volume = Volume(opts=self.child_opts)
        self.service = Service(opts=self.child_opts)

        self.register_outputs({})
