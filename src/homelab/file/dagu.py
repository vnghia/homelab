from homelab_dagu_config import DaguServiceConfigBase
from homelab_dagu_service import DaguService
from homelab_dagu_service.config.service import DaguServiceConfigBuilder
from homelab_docker.resource.service import (
    ServiceResourceBase,
    ServiceWithConfigResourceBase,
)
from pulumi import ComponentResource, ResourceOptions


class DaguFile(ComponentResource):
    RESOURCE_NAME = DaguService.name()

    def __init__(self, opts: ResourceOptions, dagu_service: DaguService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)

        for service in dagu_service.extractor_args.services.values():
            self.build_one(dagu_service, service)

        self.register_outputs({})

    def build_one(
        self, dagu_service: DaguService, service: ServiceResourceBase
    ) -> None:
        if (
            (service.name() not in dagu_service.dags)
            and isinstance(service, ServiceWithConfigResourceBase)
            and isinstance(service.config, DaguServiceConfigBase)
            and service.config.dagu
        ):
            for depend in service.config.dagu.depends_on:
                self.build_one(
                    dagu_service, dagu_service.extractor_args.services[depend]
                )

            service_opts = ResourceOptions(
                parent=ComponentResource(
                    service.name(), service.name(), None, opts=self.child_opts
                )
            )

            DaguServiceConfigBuilder(service.config.dagu).build_resources(
                opts=service_opts,
                dagu_service=dagu_service,
                extractor_args=service.extractor_args,
            )
