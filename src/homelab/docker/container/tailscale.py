import homelab_docker as docker
from pulumi import ComponentResource, ResourceOptions


class Tailscale(ComponentResource):
    RESOURCE_NAME = "tailscale"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.image = docker.image.Remote(
            repo="tailscale/tailscale",
            tag="v1.78.3",
            platform=docker.image.Platform.AMD64,
        ).build_resource(opts=self.child_opts)

        self.register_outputs({"image_repo_digest": self.image.repo_digest})
