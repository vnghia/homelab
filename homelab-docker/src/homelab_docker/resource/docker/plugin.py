import pulumi
from pulumi import ComponentResource, ResourceOptions

from ...config.docker import DockerConfig


class PluginResource(ComponentResource):
    RESOURCE_NAME = "plugin"

    def __init__(
        self,
        config: DockerConfig,
        *,
        opts: ResourceOptions,
        host: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.plugins = {
            name: model.build_resource(
                name, opts=self.child_opts, platform=config.platform
            )
            for name, model in config.plugins.root.items()
        }

        export = {name: plugin.id for name, plugin in self.plugins.items()}
        for name, value in export.items():
            pulumi.export("{}.{}.{}".format(host, self.RESOURCE_NAME, name), value)
        self.register_outputs(export)
