import homelab_docker as docker
from pulumi import ComponentResource, ResourceOptions

from homelab.common import constant


class Docker(ComponentResource):
    def __init__(self) -> None:
        super().__init__("docker", "docker", None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.bridge_network = docker.network.Bridge(
            resource_name="bridge", labels=constant.PROJECT_LABELS
        ).build_resource(opts=self.child_opts)

        self.register_outputs({"bridge_network": self.bridge_network.name})
