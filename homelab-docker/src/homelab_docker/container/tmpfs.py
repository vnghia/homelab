from pathlib import PosixPath
from typing import Any, Self

import pulumi_docker as docker
from pydantic import (
    BaseModel,
    ConfigDict,
    ModelWrapValidatorHandler,
    PositiveInt,
    model_validator,
)

from homelab_docker.pydantic.path import AbsolutePath


class Full(BaseModel):
    model_config = ConfigDict(strict=True)

    path: AbsolutePath
    size: PositiveInt | None = None


class Tmpfs(BaseModel):
    tmpfs: AbsolutePath | Full

    @model_validator(mode="wrap")
    @classmethod
    def wrap(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        return handler({"tmpfs": data})

    def to_path(self) -> PosixPath:
        tmpfs = self.tmpfs
        return tmpfs.path if isinstance(tmpfs, Full) else tmpfs

    def to_container_mount(self) -> docker.ContainerMountArgs:
        tmpfs = self.tmpfs
        size = tmpfs.size if isinstance(tmpfs, Full) else None
        return docker.ContainerMountArgs(
            target=self.to_path().as_posix(),
            type="tmpfs",
            tmpfs_options=docker.ContainerMountTmpfsOptionsArgs(size_bytes=size),
        )
