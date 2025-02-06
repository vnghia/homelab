from enum import StrEnum, auto

import pulumi_docker as docker
from pulumi import Output
from pydantic import BaseModel, PositiveInt
from pydantic_core import Url


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
    ) -> Output[Url]:
        container = self.container or router_name
        return Output.format(
            "{0}://{1}:{2}", type_.value, containers[container].name, self.port
        ).apply(Url)
