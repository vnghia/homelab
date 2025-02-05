from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from homelab_docker import model

Config = TypeVar("Config", bound=BaseModel)


class Service(BaseModel, Generic[Config]):
    platform: model.Platform
    remote: dict[str, model.RemoteImage]
    _config: Config | None = Field(None, alias="config")

    @property
    def config(self) -> Config:
        if not self._config:
            raise ValueError("`config` field is None")
        return self._config
