from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container.host import ContainerHostModeConfig
from homelab_docker.model.docker.container.network import (
    ContainerNetworkModeConfig,
    NetworkMode,
)
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic.service import (
    TraefikDynamicServiceFullModel,
    TraefikDynamicServiceModel,
    TraefikDynamicServiceType,
)
from homelab_vpn.config.service import ServiceVpnConfig
from pulumi import Output
from pydantic import AnyUrl, PositiveInt, TypeAdapter


class TraefikDynamicServiceFullModelBuilder(
    HomelabRootModel[TraefikDynamicServiceFullModel]
):
    def get_service_name(
        self, container_name: str | None, service: ServiceResourceBase
    ) -> str:
        if (
            container_name in service.containers
            or container_name in service.container_models
        ):
            return service.add_service_name(container_name)
        raise KeyError(
            "Container {} is not configured in service {}".format(
                container_name, service.name()
            )
        )

    def to_url(
        self, type_: TraefikDynamicServiceType, extractor_args: ExtractorArgs
    ) -> Output[AnyUrl]:
        root = self.root
        service = extractor_args.service

        network_config = service.container_models[root.container].network.root
        if root.external is not None:
            service_name = str(root.external)
        elif isinstance(network_config, ContainerNetworkModeConfig):
            match network_config.mode:
                case NetworkMode.VPN:
                    service_name = self.get_service_name(
                        ServiceVpnConfig.VPN_CONTAINER, service
                    )
                case NetworkMode.HOST:
                    service_name = ContainerHostModeConfig.LOCALHOST_HOST
        else:
            service_name = self.get_service_name(root.container, service)

        return Output.format(
            "{}://{}:{}",
            root.scheme or type_.value,
            service_name,
            GlobalExtractor(root.port)
            .extract_str(extractor_args)
            .apply(lambda x: TypeAdapter(PositiveInt).validate_python(int(x))),
        ).apply(AnyUrl)

    def to_service(
        self,
        type_: TraefikDynamicServiceType,
        router_name: str,
        extractor_args: ExtractorArgs,
    ) -> dict[str, Any]:
        root = self.root

        return {
            router_name: {
                "loadBalancer": {
                    "servers": [{"url": self.to_url(type_, extractor_args).apply(str)}]
                }
                | (
                    {"passHostHeader": root.pass_host_header}
                    if root.pass_host_header is not None
                    else {}
                )
            }
        }


class TraefikDynamicServiceModelBuilder(HomelabRootModel[TraefikDynamicServiceModel]):
    @property
    def full(self) -> TraefikDynamicServiceFullModel | None:
        root = self.root.root

        if isinstance(root, TraefikDynamicServiceFullModel):
            return root
        return None

    def to_service_name(self, router_name: str) -> str:
        root = self.root.root

        return (
            router_name
            if isinstance(root, (TraefikDynamicServiceFullModel, int))
            else root
        )
