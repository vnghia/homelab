from pulumi import ComponentResource, ResourceOptions

from homelab import config


class Volume(ComponentResource):
    RESOURCE_NAME = "volume"

    @classmethod
    def get_name(cls, namespace: str, name: str) -> str:
        return f"{namespace}-{name}"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.local = {
            namespace: {
                name: model.build_resource(
                    self.get_name(namespace, name), opts=self.child_opts
                )
                for name, model in volume.items()
            }
            for namespace, volume in config.docker.volume.local.items()
        }

        self.register_outputs(
            {
                self.get_name(namespace, name): volume.id
                for namespace, local in self.local.items()
                for name, volume in local.items()
            }
        )
