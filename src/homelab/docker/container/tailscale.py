from pulumi import ComponentResource, ResourceOptions


class Tailscale(ComponentResource):
    RESOURCE_NAME = "tailscale"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)
