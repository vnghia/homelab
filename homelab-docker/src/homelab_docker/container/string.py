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

    def to_str(self, volumes: dict[str, Volume] | None = None) -> str:
        data = self.data
        if isinstance(data, VolumePath):
            if volumes is None:
                raise ValueError("`volumes` is required for volume path string type")
            return data.to_str(volumes)
        else:
            return data
