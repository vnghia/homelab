from enum import StrEnum, auto
from typing import Any

from homelab_docker.model.container.extract import ContainerExtract
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pydantic import AnyUrl, PositiveInt, TypeAdapter


class TraefikDynamicServiceType(StrEnum):
    HTTP = auto()


class TraefikDynamicServiceFullModel(HomelabBaseModel):
    container: str | None = None
    port: ContainerExtract

    def to_url(
        self,
        type_: TraefikDynamicServiceType,
        main_service: ServiceResourceBase,
    ) -> AnyUrl:
        main_service.containers[self.container]
        return AnyUrl(
            "{}://{}:{}".format(
                type_.value,
                main_service.add_service_name(self.container),
                TypeAdapter(PositiveInt).validate_python(
                    int(
                        self.port.extract_str(
                            main_service.model[self.container], main_service
                        )
                    )
                ),
            )
        )

    def to_http_service(
        self,
        type_: TraefikDynamicServiceType,
        router_name: str,
        main_service: ServiceResourceBase,
    ) -> dict[str, Any]:
        return {
            router_name: {
                "loadBalancer": {
                    "servers": [{"url": str(self.to_url(type_, main_service))}]
                }
            }
        }


class TraefikDynamicServiceModel(
    HomelabRootModel[str | TraefikDynamicServiceFullModel]
):
    @property
    def full(self) -> TraefikDynamicServiceFullModel | None:
        root = self.root
        if isinstance(root, TraefikDynamicServiceFullModel):
            return root
        else:
            return None

    def to_service_name(self, router_name: str) -> str:
        root = self.root
        return (
            router_name
            if isinstance(root, (TraefikDynamicServiceFullModel, int))
            else root
        )
