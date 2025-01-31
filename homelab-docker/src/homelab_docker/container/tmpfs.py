from pathlib import PosixPath
from typing import Any, Self

import pulumi_docker as docker
from pydantic import (
    BaseModel,
    ConfigDict,
    ModelWrapValidatorHandler,
    PositiveInt,
    ValidationError,
    model_validator,
)

from homelab_docker.pydantic.path import AbsolutePath


class Full(BaseModel):
    model_config = ConfigDict(strict=True)

    path: AbsolutePath
    size: PositiveInt | None = None


class Tmpfs(BaseModel):
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

    def to_container_mount(self) -> docker.ContainerMountArgs:
        data = self.data
        size = data.size if isinstance(data, Full) else None
        return docker.ContainerMountArgs(
            target=self.to_path().as_posix(),
            type="tmpfs",
            tmpfs_options=docker.ContainerMountTmpfsOptionsArgs(size_bytes=size),
        )
