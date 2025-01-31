from typing import Any, Self

from pydantic import (
    BaseModel,
    ModelWrapValidatorHandler,
    PositiveInt,
    ValidationError,
    model_validator,
)

from homelab_docker.container.volume import Volume
from homelab_docker.volume_path import VolumePath


class String(BaseModel):
    data: PositiveInt | str | VolumePath

    @model_validator(mode="wrap")
    @classmethod
    def wrap(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        try:
            return handler(data)
        except ValidationError:
            return handler({"data": data})

    def to_str(self, volumes: dict[str, Volume] | None = None) -> str:
        data = self.data
        if isinstance(data, VolumePath):
            if volumes is None:
                raise ValueError("`volumes` is required for volume path string type")
            return data.to_str(volumes)
        else:
            return str(data)
