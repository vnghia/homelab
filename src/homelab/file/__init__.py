from homelab_traefik_service import TraefikService
from pulumi import ComponentResource, ResourceOptions

from .traefik import TraefikFile


class File(ComponentResource):
    RESOURCE_NAME = "file"

    def __init__(self, traefik_service: TraefikService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.traefik = TraefikFile(
            opts=self.child_opts, traefik_service=traefik_service
        )
        self.register_outputs({})
