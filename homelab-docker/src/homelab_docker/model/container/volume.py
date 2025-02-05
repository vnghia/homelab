from pathlib import PosixPath
from typing import Any, ClassVar, Self

import pulumi_docker as docker
from pulumi import Input
from pydantic import (
    BaseModel,
    ModelWrapValidatorHandler,
    model_validator,
)

from homelab_docker.pydantic import AbsolutePath


class DockerConfig(BaseModel):
    DOCKER_SOCKET_PATH: ClassVar[AbsolutePath] = PosixPath("/var/run/docker.sock")

    docker_read_only: bool = True

    def to_container_path(self) -> PosixPath:
        return self.DOCKER_SOCKET_PATH

    def to_args(self, _: Input[str]) -> docker.ContainerVolumeArgs:
        return docker.ContainerVolumeArgs(
            container_path=self.to_container_path().as_posix(),
            host_path=self.DOCKER_SOCKET_PATH.as_posix(),
            read_only=self.docker_read_only,
        )


class VolumeConfig(BaseModel):
    path: AbsolutePath
    read_only: bool = False

    def to_container_path(self) -> PosixPath:
        return self.path

    def to_args(self, volume_name: Input[str]) -> docker.ContainerVolumeArgs:
        return docker.ContainerVolumeArgs(
            container_path=self.to_container_path().as_posix(),
            read_only=self.read_only,
            volume_name=volume_name,
        )


class Volume(BaseModel):
    data: AbsolutePath | DockerConfig | VolumeConfig

    @model_validator(mode="wrap")
    @classmethod
    def wrap(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        if isinstance(data, (PosixPath, DockerConfig, VolumeConfig)):
            return cls(data=data)
        else:
            return handler({"data": data})

    def to_container_path(self) -> PosixPath:
        data = self.data
        if isinstance(data, PosixPath):
            return data
        else:
            return data.to_container_path()

    def to_args(self, volume_name: Input[str]) -> docker.ContainerVolumeArgs:
        data = self.data
        if isinstance(data, PosixPath):
            return docker.ContainerVolumeArgs(
                container_path=data.as_posix(), volume_name=volume_name
            )
        else:
            return data.to_args(volume_name)
