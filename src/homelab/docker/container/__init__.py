from pulumi import ComponentResource, ResourceOptions

from homelab.docker.container.tailscale import Tailscale


class Container(ComponentResource):
    RESOURCE_NAME = "container"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.tailscale = Tailscale(opts=self.child_opts)

        self.register_outputs({})
