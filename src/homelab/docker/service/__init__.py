from pulumi import ComponentResource, ResourceOptions

from homelab.docker.image import Image
from homelab.docker.service.tailscale import Tailscale
from homelab.docker.volume import Volume


class Service(ComponentResource):
    RESOURCE_NAME = "service"

    def __init__(
        self, image: Image, volume: Volume, opts: ResourceOptions | None
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.tailscale = Tailscale(image=image, volume=volume, opts=self.child_opts)

        self.register_outputs({})
