from typing import Any, Self

from pydantic import BaseModel, ModelWrapValidatorHandler, model_validator

from homelab_docker.container.volume import Volume
from homelab_docker.volume_path import VolumePath


class String(BaseModel):
    data: str | VolumePath

    @model_validator(mode="wrap")
    @classmethod
    def wrap(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        return handler({"data": data})

    def to_str(self, volumes: dict[str, Volume]) -> str:
        data = self.data
        return data.to_str(volumes) if isinstance(data, VolumePath) else data
