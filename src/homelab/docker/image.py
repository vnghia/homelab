import pulumi
from homelab_config import config
from pulumi import ComponentResource, ResourceOptions


class Image(ComponentResource):
    RESOURCE_NAME = "image"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.remotes = {
            name: model.build_resource(name, opts=self.child_opts)
            for name, model in config.docker.images.items()
        }
        for name, image in self.remotes.items():
            pulumi.export("image-{}".format(name), image.image_id)

        self.register_outputs(
            {name: image.repo_digest for name, image in self.remotes.items()}
        )
