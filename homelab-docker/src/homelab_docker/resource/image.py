import pulumi
from pulumi import ComponentResource, ResourceOptions

from homelab_docker import config


class Image(ComponentResource):
    RESOURCE_NAME = "image"

    def __init__(
        self,
        config: config.Image,
        *,
        opts: ResourceOptions,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.remotes = {
            name: model.build_resource(
                name, opts=self.child_opts, platform=config.platform
            )
            for name, model in config.remote.items()
        }

        export = {name: image.id for name, image in self.remotes.items()}
        pulumi.export(self.RESOURCE_NAME, export)
        self.register_outputs(export)
