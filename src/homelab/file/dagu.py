from homelab_dagu_service import DaguService
from homelab_dagu_service.config.service import DaguServiceConfigBuilder
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ComponentResource, ResourceOptions


class DaguFile(ComponentResource):
    RESOURCE_NAME = DaguService.name()

    def __init__(self, opts: ResourceOptions, dagu_service: DaguService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)
        self.dagu_service = dagu_service

    def build_one(self, service: ServiceResourceBase) -> None:
        if (service.name() not in self.dagu_service.dags) and (
            dagu_service_config := self.dagu_service.get_service_config(service)
        ):
            for depend in dagu_service_config.depends_on:
                self.build_one(self.dagu_service.extractor_args.services[depend])

            service_opts = ResourceOptions(
                parent=ComponentResource(
                    service.name(), service.name(), None, opts=self.child_opts
                )
            )

            DaguServiceConfigBuilder(dagu_service_config).build_resources(
                opts=service_opts,
                dagu_service=self.dagu_service,
                extractor_args=service.extractor_args,
            )
