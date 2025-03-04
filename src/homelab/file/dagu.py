from homelab_dagu_config import DaguServiceConfigBase
from homelab_dagu_service import DaguService
from homelab_dagu_service.config.service import DaguServiceConfigBuilder
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ComponentResource, ResourceOptions


class DaguFile(ComponentResource):
    RESOURCE_NAME = DaguService.name()

    def __init__(self, opts: ResourceOptions | None, dagu_service: DaguService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)

        for service in ServiceWithConfigResourceBase.SERVICES.values():
            if isinstance(service, ServiceWithConfigResourceBase) and isinstance(
                service.config, DaguServiceConfigBase
            ):
                if service.config.dagu:
                    service_opts = ResourceOptions(
                        parent=ComponentResource(
                            service.name(), service.name(), None, opts=self.child_opts
                        )
                    )

                    DaguServiceConfigBuilder(service.config.dagu).build_resources(
                        opts=service_opts,
                        main_service=service,
                        dagu_service=dagu_service,
                    )

        self.register_outputs({})
