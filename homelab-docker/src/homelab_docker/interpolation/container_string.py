from typing import Any, Self

from pydantic import BaseModel, ModelWrapValidatorHandler, PositiveInt, model_validator

from homelab_docker.interpolation.volume_path import VolumePath
from homelab_docker.model.container.volume import Volume as ContainerVolume


class ContainerString(BaseModel):
    data: PositiveInt | str | VolumePath

    @model_validator(mode="wrap")
    @classmethod
    def wrap(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        if isinstance(data, (int, str, VolumePath)):
            return cls(data=data)
        else:
            return handler({"data": data})

    def to_str(
        self, container_volumes: dict[str, ContainerVolume] | None = None
    ) -> str:
        data = self.data
        if isinstance(data, VolumePath):
            return data.to_container_path(container_volumes or {}).as_posix()
        else:
            return str(data)
