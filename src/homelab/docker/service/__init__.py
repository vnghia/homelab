from pulumi import ComponentResource, ResourceOptions

from homelab.docker.resource import Resource
from homelab.docker.service.dozzle import Dozzle
from homelab.docker.service.tailscale import Tailscale
from homelab.docker.service.traefik import Traefik


class Service(ComponentResource):
    RESOURCE_NAME = "service"

    def __init__(
        self,
        resource: Resource,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.tailscale = Tailscale(resource=resource, opts=self.child_opts)
        self.dozzle = Dozzle(resource=resource, opts=self.child_opts)
        self.traefik = Traefik(resource=resource, opts=self.child_opts)

        self.register_outputs({})
