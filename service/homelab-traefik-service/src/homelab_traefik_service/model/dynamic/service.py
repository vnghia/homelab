from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.container.network import (
    ContainerNetworkModeConfig,
    NetworkMode,
)
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic.service import (
    TraefikDynamicServiceFullModel,
    TraefikDynamicServiceModel,
    TraefikDynamicServiceType,
)
from pulumi import Output
from pydantic import AnyUrl, PositiveInt, TypeAdapter


class TraefikDynamicServiceFullModelBuilder(
    HomelabRootModel[TraefikDynamicServiceFullModel]
):
    def to_url(
        self, type_: TraefikDynamicServiceType, extractor_args: ExtractorArgs
    ) -> Output[AnyUrl]:
        root = self.root
        service = extractor_args.service

        network_config = service.model.containers[root.container].network.root
        if root.external is not None:
            service_name = str(root.external)
        elif isinstance(network_config, ContainerNetworkModeConfig):
            match network_config.mode:
                case NetworkMode.VPN:
                    vpn_config = extractor_args.docker_resource_args.config.vpn_
                    vpn_service = service.SERVICES[vpn_config.service]
                    vpn_service.containers[vpn_config.container]
                    service_name = vpn_service.add_service_name(vpn_config.container)
                case NetworkMode.HOST:
                    service_name = "host.docker.internal"
        else:
            service.containers[root.container]
            service_name = service.add_service_name(root.container)

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
