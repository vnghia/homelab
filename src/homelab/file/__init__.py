from homelab_dagu_service import DaguService
from homelab_traefik_service import TraefikService
from pulumi import ComponentResource, ResourceOptions

from .dagu import DaguFile
from .traefik import TraefikFile


class File(ComponentResource):
    RESOURCE_NAME = "file"

    def __init__(
        self, traefik_service: TraefikService, dagu_service: DaguService
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.traefik = TraefikFile(
            opts=self.child_opts, traefik_service=traefik_service
        )
        self.dagu = DaguFile(opts=self.child_opts, dagu_service=dagu_service)
        self.register_outputs({})
