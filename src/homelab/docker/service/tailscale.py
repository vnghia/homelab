from pulumi import ComponentResource, ResourceOptions

from homelab import config
from homelab.docker.image import Image


class Tailscale(ComponentResource):
    RESOURCE_NAME = "tailscale"

    def __init__(self, image: Image, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.container = (
            config.docker.services[self.RESOURCE_NAME]
            .containers[self.RESOURCE_NAME]
            .build_resource(self.RESOURCE_NAME, image.image, opts=self.child_opts)
        )

        self.register_outputs({})
