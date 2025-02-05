import pulumi
import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from homelab_docker import config


class Network(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(
        self,
        config: config.Network,
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

        export = {
            config.DEFAULT_BRIDGE: self.default_bridge.name,
            config.INTERNAL_BRIDGE: self.internal_bridge.name,
        }
        pulumi.export(self.RESOURCE_NAME, export)
        self.register_outputs(export)

    @property
    def default_bridge_args(self) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(name=self.default_bridge.name)

    @property
    def internal_bridge_args(self) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(name=self.internal_bridge.name)
