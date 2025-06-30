from typing import Any

from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.container.network import (
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
from pulumi import Output
from pydantic import AnyUrl, PositiveInt, TypeAdapter


class TraefikDynamicServiceFullModelBuilder(
    HomelabRootModel[TraefikDynamicServiceFullModel]
):
    def to_url(
        self,
        type_: TraefikDynamicServiceType,
        main_service: ServiceResourceBase,
    ) -> Output[AnyUrl]:
        root = self.root

        network_config = main_service.model.containers[root.container].network.root
        if (
            isinstance(network_config, ContainerNetworkModeConfig)
            and network_config.mode == NetworkMode.VPN
        ):
            vpn_config = main_service.docker_resource_args.config.vpn
            vpn_service = main_service.SERVICES[vpn_config.service]
            vpn_service.containers[vpn_config.container]
            service_name = vpn_service.add_service_name(vpn_config.container)
        else:
            main_service.containers[root.container]
            service_name = main_service.add_service_name(root.container)

        return Output.format(
            "{}://{}:{}",
            root.scheme or type_.value,
            service_name,
            GlobalExtractor(root.port)
            .extract_str(main_service, main_service.model[root.container])
            .apply(lambda x: TypeAdapter(PositiveInt).validate_python(int(x))),
        ).apply(AnyUrl)

    def to_service(
        self,
        type_: TraefikDynamicServiceType,
        router_name: str,
        main_service: ServiceResourceBase,
    ) -> dict[str, Any]:
        return {
            router_name: {
                "loadBalancer": {
                    "servers": [{"url": self.to_url(type_, main_service).apply(str)}]
                }
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
