from enum import StrEnum, auto
from typing import Any

from homelab_docker.resource.service import ServiceResourceArgs
from pydantic import AnyUrl, BaseModel, PositiveInt, RootModel


class TraefikDynamicServiceType(StrEnum):
    HTTP = auto()


class TraefikDynamicServiceFullConfig(BaseModel):
    container: str | None = None
    port: PositiveInt

    def to_url(
        self,
        type_: TraefikDynamicServiceType,
        router_name: str,
        service_resource_args: ServiceResourceArgs,
    ) -> AnyUrl:
        container = self.container or router_name
        service_resource_args.containers[container]
        return AnyUrl("{}://{}:{}".format(type_.value, container, self.port))

    def to_http_service(
        self,
        type_: TraefikDynamicServiceType,
        router_name: str,
        service_resource_args: ServiceResourceArgs,
    ) -> dict[str, Any]:
        return {
            router_name: {
                "loadBalancer": {
                    "servers": [
                        {
                            "url": str(
                                self.to_url(type_, router_name, service_resource_args)
                            )
                        }
                    ]
                }
            }
        }


class TraefikDynamicServiceConfig(
    RootModel[str | PositiveInt | TraefikDynamicServiceFullConfig]
):
    @property
    def full(self) -> TraefikDynamicServiceFullConfig | None:
        root = self.root
        if isinstance(root, int):
            return TraefikDynamicServiceFullConfig(port=root)
        elif isinstance(root, TraefikDynamicServiceFullConfig):
            return root
        else:
            return None

    def to_service_name(self, router_name: str) -> str:
        root = self.root
        return (
            router_name
            if isinstance(root, (TraefikDynamicServiceFullConfig, int))
            else root
        )
