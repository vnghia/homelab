import typing

from pulumi import ComponentResource, ResourceOptions

from homelab.file.hatchet import HatchetFile

from .traefik import TraefikFile
from .vector import VectorFile

if typing.TYPE_CHECKING:
    from ..host import HostBaseNoConfig


class File(ComponentResource):
    RESOURCE_NAME = "file"

    def __init__(self, *, opts: ResourceOptions, host: HostBaseNoConfig) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.traefik = TraefikFile(opts=self.child_opts, traefik_service=host.traefik)
        self.vector = VectorFile(opts=self.child_opts, vector_service=host.vector)
        self.hatchet = HatchetFile(opts=self.child_opts, hatchet_service=host.hatchet)

        self.traefik.build_one(host.traefik)
        for service in host.extractor_args.services.values():
            self.traefik.build_one(service)
            self.hatchet.build_one(service)
            if service.name() != host.vector.name():
                self.vector.build_one(service)
        self.vector.build_one(host.vector)

        self.vector.finalize()

        self.traefik.register_outputs({})
        self.register_outputs({})
