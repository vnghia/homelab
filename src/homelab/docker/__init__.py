import homelab_docker as docker
from pulumi import ComponentResource, ResourceOptions

from homelab.common import constant
from homelab.docker.container import Container
from homelab.docker.image import Image


class Docker(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(self) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.bridge_network = docker.network.Bridge(
            resource_name="bridge", labels=constant.PROJECT_LABELS
        ).build_resource(opts=self.child_opts)

        self.image = Image(opts=self.child_opts)

        self.container = Container(opts=self.child_opts)

        self.register_outputs({"bridge_network": self.bridge_network.name})
