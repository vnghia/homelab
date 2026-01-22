from homelab_docker.config.docker.network import NetworkEgressType
from homelab_docker.resource.service import ServiceResourceBase
from homelab_extract import GlobalExtract
from homelab_extract.host import HostExtract, HostExtractSource
from homelab_extract.host.network import HostExtractNetworkSource, HostNetworkInfoSource
from homelab_traefik_config import TraefikServiceConfig, TraefikServiceDynamicConfig
from homelab_traefik_config.model.dynamic import TraefikDynamicModel
from homelab_traefik_config.model.dynamic.middleware import (
    TraefikDynamicMiddlewareBuildModel,
    TraefikDynamicMiddlewareModel,
    TraefikDynamicMiddlewareUseModel,
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
    EGRESS_LOCAL_MIDDLEWARE_NAME = "egress-local"

    def __init__(self, opts: ResourceOptions, traefik_service: TraefikService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)
        self.traefik_service = traefik_service

    def get_egress_name(self, egress: str) -> str:
        return "egress-{}".format(egress)

    def get_egress_proxy(self, type: NetworkEgressType) -> str:
        return "egress-{}-proxy".format(type)

    def build_service_dynamic(
        self, service: ServiceResourceBase
    ) -> dict[str | None, TraefikDynamicModel]:
        egresses = (
            self.traefik_service.extractor_args.host.docker.network.service_egresses
        )
        dynamic: dict[str | None, TraefikDynamicModel] = {}

        service_name = service.name()
        if service_name in egresses:
            dynamic[self.EGRESS_LOCAL_MIDDLEWARE_NAME] = TraefikDynamicModel(
                TraefikDynamicMiddlewareBuildModel(
                    type=TraefikDynamicType.TCP,
                    name=self.EGRESS_LOCAL_MIDDLEWARE_NAME,
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
            egress_middlewares = [
                TraefikDynamicMiddlewareModel(
                    TraefikDynamicMiddlewareUseModel(
                        name=self.EGRESS_LOCAL_MIDDLEWARE_NAME,
                    )
                )
            ]

            for egress_type, egress in egresses[service_name].items():
                egress_entrypoint = self.traefik_service.config.entrypoint.egress_[
                    egress_type
                ]

                match egress_type:
                    case NetworkEgressType.HTTPS:
                        proxies = []
                        for egress_key, egress_model in egress.items():
                            if egress_model.proxied:
                                proxies.extend(egress_model.addresses)
                                continue

                            egress_name = self.get_egress_name(egress_key)
                            dynamic[egress_name] = TraefikDynamicModel(
                                TraefikDynamicTcpModel(
                                    name=egress_name,
                                    entrypoint=egress_entrypoint,
                                    service=TraefikDynamicServiceModel(
                                        TraefikDynamicServiceFullModel(
                                            external=egress_model.ip
                                            or egress_model.addresses[0],
                                            port=None,
                                        )
                                    ),
                                    hostsni=egress_model.addresses,
                                    middlewares=egress_middlewares,
                                )
                            )
                        if proxies:
                            egress_proxy = self.traefik_service.extractor_args.host.docker.network.config.egress[
                                egress_type
                            ]
                            egress_name = self.get_egress_proxy(egress_type)
                            dynamic[egress_name] = TraefikDynamicModel(
                                TraefikDynamicTcpModel(
                                    name=egress_name,
                                    entrypoint=egress_entrypoint,
                                    service=TraefikDynamicServiceModel(
                                        TraefikDynamicServiceFullModel(
                                            service=egress_proxy.service,
                                            container=egress_proxy.container,
                                            port=egress_proxy.port.with_service(
                                                egress_proxy.service, False
                                            ),
                                        )
                                    ),
                                    hostsni=proxies,
                                    middlewares=egress_middlewares,
                                )
                            )

        return dynamic

    def build_one(self, service: ServiceResourceBase) -> None:
        if (
            service.name() not in self.traefik_service.routers
            and service.name() not in self.traefik_service.middlewares
        ):
            service_dynamic = self.build_service_dynamic(service)

            if (
                traefik_service_config := self.traefik_service.get_service_config(
                    service
                )
            ) and service_dynamic:
                traefik_service_config = traefik_service_config.__replace__(
                    dynamic=traefik_service_config.dynamic | service_dynamic
                )
            elif service_dynamic:
                traefik_service_config = TraefikServiceConfig(
                    dynamic=TraefikServiceDynamicConfig(service_dynamic)
                )

            if traefik_service_config:
                for depend in traefik_service_config.depends_on:
                    self.build_one(self.traefik_service.extractor_args.services[depend])

                service_opts = ResourceOptions(
                    parent=ComponentResource(
                        service.name(), service.name(), None, opts=self.child_opts
                    )
                )

                TraefikServiceConfigBuilder(traefik_service_config).build_resources(
                    opts=service_opts,
                    traefik_service=self.traefik_service,
                    extractor_args=service.extractor_args,
                )
