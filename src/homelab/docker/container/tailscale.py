from pulumi import ComponentResource, ResourceOptions

from homelab import config


class Tailscale(ComponentResource):
    RESOURCE_NAME = "tailscale"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.image = config.docker.image[self.RESOURCE_NAME].build_resource(
            opts=self.child_opts
        )

        self.register_outputs({"image_repo_digest": self.image.repo_digest})
