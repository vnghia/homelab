from homelab_docker.resource.service import ServiceResourceBase
from homelab_hatchet_service import HatchetService
from homelab_hatchet_service.model import HatchetServiceBuilder
from pulumi import ComponentResource, ResourceOptions


class HatchetFile(ComponentResource):
    RESOURCE_NAME = HatchetService.name()

    def __init__(
        self, opts: ResourceOptions, hatchet_service: HatchetService | None
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)
        self.hatchet_service = hatchet_service

    def build_one(self, service: ServiceResourceBase) -> None:
        if self.hatchet_service and (
            hatchet_service_config := self.hatchet_service.get_service_config(service)
        ):
            service_opts = ResourceOptions(
                parent=ComponentResource(
                    service.name(), service.name(), None, opts=self.child_opts
                )
            )

            HatchetServiceBuilder(hatchet_service_config).build_resources(
                opts=service_opts,
                hatchet_service=self.hatchet_service,
                extractor_args=service.extractor_args,
            )
