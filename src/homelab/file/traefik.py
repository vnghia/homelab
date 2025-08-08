from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_traefik_config import TraefikServiceConfigBase
from homelab_traefik_service import TraefikService
from homelab_traefik_service.config.service import TraefikServiceConfigBuilder
from pulumi import ComponentResource, ResourceOptions


class TraefikFile(ComponentResource):
    RESOURCE_NAME = TraefikService.name()

    def __init__(self, opts: ResourceOptions, traefik_service: TraefikService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)

        for service in traefik_service.extractor_args.services.values():
            if (
                isinstance(service, ServiceWithConfigResourceBase)
                and isinstance(service.config, TraefikServiceConfigBase)
                and service.config.traefik
            ):
                service_opts = ResourceOptions(
                    parent=ComponentResource(
                        service.name(), service.name(), None, opts=self.child_opts
                    )
                )

                TraefikServiceConfigBuilder(service.config.traefik).build_resources(
                    opts=service_opts,
                    traefik_service=traefik_service,
                    extractor_args=service.extractor_args,
                )

        self.register_outputs({})
