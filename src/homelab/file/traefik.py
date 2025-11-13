from homelab_docker.config.service.network import ServiceNetworkProxyEgressType
from homelab_docker.resource.service import (
    ServiceResourceBase,
    ServiceWithConfigResourceBase,
)
from homelab_extract import GlobalExtract
from homelab_extract.host import HostExtract, HostExtractSource
from homelab_extract.host.network import HostExtractNetworkSource, HostNetworkInfoSource
from homelab_traefik_config import (
    TraefikServiceConfig,
    TraefikServiceConfigBase,
    TraefikServiceDynamicConfig,
)
from homelab_traefik_config.model.dynamic import TraefikDynamicModel
from homelab_traefik_config.model.dynamic.middleware import (
    TraefikDynamicMiddlewareBuildModel,
    TraefikDynamicMiddlewareModel,
)
from homelab_traefik_config.model.dynamic.middleware.ipwhitelist import (
    TraefikDynamicMiddlewareIpWhitelistModel,
)
from homelab_traefik_config.model.dynamic.service import (
    TraefikDynamicServiceFullModel,
    TraefikDynamicServiceModel,
)
from homelab_traefik_config.model.dynamic.tcp import TraefikDynamicTcpModel
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType
from homelab_traefik_service import TraefikService
from homelab_traefik_service.config.service import TraefikServiceConfigBuilder
from pulumi import ComponentResource, ResourceOptions


class TraefikFile(ComponentResource):
    RESOURCE_NAME = TraefikService.name()

    def __init__(self, opts: ResourceOptions, traefik_service: TraefikService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)

        self.build_one(traefik_service, traefik_service)
        for service in traefik_service.extractor_args.services.values():
            self.build_one(traefik_service, service)

        self.register_outputs({})

    def get_egress_name(self, egress: str) -> str:
        return "egress-{}".format(egress)

    def get_egress_local_name(self, egress: str) -> str:
        return "{}-local".format(egress)

    def build_service_dynamic(
        self, traefik_service: TraefikService, service: ServiceResourceBase
    ) -> dict[str | None, TraefikDynamicModel]:
        egresses = traefik_service.extractor_args.host.docker.network.service_egresses
        dynamic: dict[str | None, TraefikDynamicModel] = {}

        service_name = service.name()
        if service_name in egresses:
            for egress_type, egress in egresses[service_name].items():
                for egress_key, egress_model in egress.items():
                    egress_name = self.get_egress_name(egress_key)
                    match egress_type:
                        case ServiceNetworkProxyEgressType.HTTPS:
                            dynamic[egress_name] = TraefikDynamicModel(
                                TraefikDynamicTcpModel(
                                    name=egress_name,
                                    address=egress_model,
                                    entrypoint=traefik_service.config.entrypoint.egress_[
                                        egress_type
                                    ],
                                    service=TraefikDynamicServiceModel(
                                        TraefikDynamicServiceFullModel(
                                            external=egress_model, port=None
                                        )
                                    ),
                                    hostsni=None,
                                    middlewares=[
                                        TraefikDynamicMiddlewareModel(
                                            TraefikDynamicMiddlewareBuildModel(
                                                type=TraefikDynamicType.TCP,
                                                name=self.get_egress_local_name(
                                                    egress_name
                                                ),
                                                data=TraefikDynamicMiddlewareIpWhitelistModel(
                                                    source_range=GlobalExtract(
                                                        HostExtract(
                                                            HostExtractSource(
                                                                HostExtractNetworkSource(
                                                                    network=service_name,
                                                                    info=HostNetworkInfoSource.SUBNET,
                                                                )
                                                            )
                                                        )
                                                    )
                                                ),
                                            )
                                        )
                                    ],
                                )
                            )

        return dynamic

    def build_one(
        self, traefik_service: TraefikService, service: ServiceResourceBase
    ) -> None:
        if (
            service.name() not in traefik_service.routers
            and service.name() not in traefik_service.middlewares
        ):
            service_dynamic = self.build_service_dynamic(traefik_service, service)

            traefik_service_config = None
            if (
                isinstance(service, ServiceWithConfigResourceBase)
                and isinstance(service.config, TraefikServiceConfigBase)
                and service.config.traefik.dynamic
            ):
                traefik_service_config = service.config.traefik
                if service_dynamic:
                    traefik_service_config = service.config.traefik.__replace__(
                        dynamic=traefik_service_config.dynamic | service_dynamic
                    )
            elif service_dynamic:
                traefik_service_config = TraefikServiceConfig(
                    dynamic=TraefikServiceDynamicConfig(service_dynamic)
                )

            if traefik_service_config:
                for depend in traefik_service_config.depends_on:
                    self.build_one(
                        traefik_service, traefik_service.extractor_args.services[depend]
                    )

                service_opts = ResourceOptions(
                    parent=ComponentResource(
                        service.name(), service.name(), None, opts=self.child_opts
                    )
                )

                TraefikServiceConfigBuilder(traefik_service_config).build_resources(
                    opts=service_opts,
                    traefik_service=traefik_service,
                    extractor_args=service.extractor_args,
                )
