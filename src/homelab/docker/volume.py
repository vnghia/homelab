from pulumi import ComponentResource, ResourceOptions

from homelab import config


class Volume(ComponentResource):
    RESOURCE_NAME = "volume"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.volumes = {
            name: model.build_resource(name, opts=self.child_opts)
            for name, model in config.docker.volumes.local.items()
        }

        self.register_outputs(
            {name: volume.name for name, volume in self.volumes.items()}
        )
