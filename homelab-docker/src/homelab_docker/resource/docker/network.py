import pulumi
import pulumi_docker as docker
from homelab_global import GlobalArgs
from pulumi import ComponentResource, Input, ResourceOptions

from ...config.docker.network import NetworkConfig


class NetworkResource(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions,
        global_args: GlobalArgs,
        host: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.bridge = {
            key: model.build_resource(
                self.get_bridge_name(key),
                opts=self.child_opts,
                project_labels=global_args.project.labels,
            )
            for key, model in config.bridge.items()
        }

        for value in self.bridge.values():
            pulumi.export(
                "{}.{}.{}".format(host, self.RESOURCE_NAME, value._name), value.name
            )
        self.register_outputs({})

    @classmethod
    def get_bridge_name(cls, name: str) -> str:
        return "{}-bridge".format(name)

    def get_bridge_args(
        self, name: str, aliases: list[Input[str]]
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(
            name=self.bridge[name].name, aliases=aliases
        )
