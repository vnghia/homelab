from typing import Any, Type, TypeVar

import homelab_docker as docker
from pydantic import BaseModel, Field

Config = TypeVar("Config", bound=BaseModel)


class Service(BaseModel):
    raw_config: Any = Field(None, alias="config")
    container: docker.container.Container
    containers: dict[str, docker.container.Container] = {}

    def config(self, type_: Type[Config]) -> Config:
        return type_.model_validate(self.raw_config)
