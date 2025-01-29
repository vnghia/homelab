from pulumi import ResourceOptions

from homelab.docker.resource import Resource
from homelab.docker.service.base import Base


class Traefik(Base):
    def __init__(
        self,
        resource: Resource,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(resource=resource, opts=opts)

        self.build_containers()
