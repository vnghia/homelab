from pulumi import ResourceOptions

from homelab.docker.resource import Resource
from homelab.docker.service.base import Base
from homelab.docker.service.tailscale import Tailscale
from homelab.docker.service.traefik.config.static import Static


class Traefik(Base):
    def __init__(
        self,
        resource: Resource,
        tailscale: Tailscale,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(resource=resource, opts=opts)

        self.static = Static(self.config(), tailscale)
        self.build_containers()
