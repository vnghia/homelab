from pathlib import PosixPath
from typing import Any, Self

import pulumi_docker as docker
from pulumi import Input
from pydantic import BaseModel, ConfigDict, ModelWrapValidatorHandler, model_validator

from homelab_docker.pydantic.path import AbsolutePath


class Full(BaseModel):
    model_config = ConfigDict(strict=True)

    path: AbsolutePath
    read_only: bool = False


class Volume(BaseModel):
    volume: AbsolutePath | Full

    @model_validator(mode="wrap")
    @classmethod
    def wrap(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        return handler({"volume": data})

    def to_path(self) -> PosixPath:
        volume = self.volume
        return volume.path if isinstance(volume, Full) else volume

    def to_container_volume(self, name: Input[str]) -> docker.ContainerVolumeArgs:
        volume = self.volume
        container_path = self.to_path().as_posix()
        read_only = volume.read_only if isinstance(volume, Full) else None
        return docker.ContainerVolumeArgs(
            container_path=container_path, read_only=read_only, volume_name=name
        )
