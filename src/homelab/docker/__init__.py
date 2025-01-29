from pulumi import ComponentResource, ResourceOptions

from homelab.docker.resource import Resource
from homelab.docker.service import Service


class Docker(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(self) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.resource = Resource(opts=self.child_opts)
        self.service = Service(resource=self.resource, opts=self.child_opts)

        self.register_outputs({})
