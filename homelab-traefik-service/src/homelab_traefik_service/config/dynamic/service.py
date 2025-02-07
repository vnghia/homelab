from enum import StrEnum, auto

import pulumi_docker as docker
from pydantic import AnyUrl, BaseModel, PositiveInt


class TraefikServiceType(StrEnum):
    HTTP = auto()


class TraefikService(BaseModel):
    container: str | None = None
    port: PositiveInt

    def to_url(
        self,
        type_: TraefikServiceType,
        router_name: str,
        containers: dict[str, docker.Container],
    ) -> AnyUrl:
        container = self.container or router_name
        containers[container]
        return AnyUrl("{}://{}:{}".format(type_.value, container, self.port))
