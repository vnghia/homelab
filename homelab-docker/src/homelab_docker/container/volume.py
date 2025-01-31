from pathlib import PosixPath
from typing import Any, Self

import pulumi_docker as docker
from pulumi import Input
from pydantic import (
    BaseModel,
    ConfigDict,
    ModelWrapValidatorHandler,
    ValidationError,
    model_validator,
)

from homelab_docker.pydantic.path import AbsolutePath


class Full(BaseModel):
    model_config = ConfigDict(strict=True)

    path: AbsolutePath
    read_only: bool = False


class Volume(BaseModel):
    data: AbsolutePath | Full

    @model_validator(mode="wrap")
    @classmethod
    def wrap(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        try:
            return handler(data)
        except ValidationError:
            return handler({"data": data})

    def to_path(self) -> PosixPath:
        data = self.data
        return data.path if isinstance(data, Full) else data

    def to_container_volume(self, name: Input[str]) -> docker.ContainerVolumeArgs:
        data = self.data
        container_path = self.to_path().as_posix()
        read_only = data.read_only if isinstance(data, Full) else None
        return docker.ContainerVolumeArgs(
            container_path=container_path, read_only=read_only, volume_name=name
        )
