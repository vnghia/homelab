import homelab_docker as docker
from pulumi import ComponentResource, ResourceOptions

from homelab.common import constant


class Network(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.bridge = docker.network.Bridge(
            labels=constant.PROJECT_LABELS
        ).build_resource(resource_name="bridge", opts=self.child_opts)

        self.register_outputs({"bridge": self.bridge.name})
