from typing import Any, Self, Type, TypeVar

import homelab_docker as docker
from pydantic import BaseModel, Field, model_validator

from homelab.common import constant

Config = TypeVar("Config", bound=BaseModel)


class Service(BaseModel):
    raw_config: Any = Field(None, alias="config")
    container: docker.container.Container
    containers: dict[str, docker.container.Container] = {}

    @model_validator(mode="after")
    def merge_pulumi_label(self) -> Self:
        self.container = self.container.model_copy(
            update={"labels": self.container.labels | constant.PROJECT_LABELS}
        )
        self.containers = {
            name: model.model_copy(
                update={"labels": model.labels | constant.PROJECT_LABELS}
            )
            for name, model in self.containers.items()
        }
        return self

    def config(self, type_: Type[Config]) -> Config:
        return type_.model_validate(self.raw_config)
