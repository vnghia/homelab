from pulumi import ComponentResource, ResourceOptions

from homelab import config


class Image(ComponentResource):
    RESOURCE_NAME = "image"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.image = {
            name: model.build_resource(opts=self.child_opts)
            for name, model in config.docker.image.items()
        }

        self.register_outputs(
            {name: image.repo_digest for name, image in self.image.items()}
        )
