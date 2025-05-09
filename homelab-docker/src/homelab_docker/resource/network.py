import pulumi
import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from ..config.network import NetworkConfig


class NetworkResource(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions,
        project_labels: dict[str, str],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.default_bridge = config.default_bridge.build_resource(
            config.DEFAULT_BRIDGE, opts=self.child_opts, project_labels=project_labels
        )
        self.internal_bridge = config.internal_bridge.build_resource(
            config.INTERNAL_BRIDGE, opts=self.child_opts, project_labels=project_labels
        )
        self.proxy_bridge = config.proxy_bridge.build_resource(
            config.PROXY_BRIDGE, opts=self.child_opts, project_labels=project_labels
        )

        export = {
            config.DEFAULT_BRIDGE: self.default_bridge.name,
            config.INTERNAL_BRIDGE: self.internal_bridge.name,
            config.PROXY_BRIDGE: self.proxy_bridge.name,
        }
        for name, value in export.items():
            pulumi.export("{}.{}".format(self.RESOURCE_NAME, name), value)
        self.register_outputs(export)

    def default_bridge_args(
        self, aliases: list[str]
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(
            name=self.default_bridge.name, aliases=aliases
        )

    def internal_bridge_args(
        self, aliases: list[str]
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(
            name=self.internal_bridge.name, aliases=aliases
        )

    def proxy_bridge_args(
        self, aliases: list[str]
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(
            name=self.proxy_bridge.name, aliases=aliases
        )
