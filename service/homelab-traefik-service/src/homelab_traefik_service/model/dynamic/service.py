from typing import Any

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

        main_service.containers[root.container]
        return Output.format(
            "{}://{}:{}",
            type_.value,
            main_service.add_service_name(root.container),
            root.port.extract_str(main_service).apply(
                lambda x: TypeAdapter(PositiveInt).validate_python(int(x))
            ),
        ).apply(AnyUrl)

    def to_http_service(
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
        else:
            return None

    def to_service_name(self, router_name: str) -> str:
        root = self.root.root

        return (
            router_name
            if isinstance(root, (TraefikDynamicServiceFullModel, int))
            else root
        )
