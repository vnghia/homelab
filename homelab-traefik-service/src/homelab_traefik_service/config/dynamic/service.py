from enum import StrEnum, auto
from typing import Any

import pulumi_docker as docker
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
        containers: dict[str, docker.Container],
    ) -> AnyUrl:
        container = self.container or router_name
        containers[container]
        return AnyUrl("{}://{}:{}".format(type_.value, container, self.port))

    def to_http_service(
        self,
        type_: TraefikDynamicServiceType,
        router_name: str,
        containers: dict[str, docker.Container],
    ) -> dict[str, Any]:
        return {
            router_name: {
                "loadBalancer": {
                    "servers": [
                        {"url": str(self.to_url(type_, router_name, containers))}
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
