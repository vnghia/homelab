from pathlib import PosixPath
from typing import ClassVar

import pulumi_docker as docker
from pulumi import Input
from pydantic import BaseModel, RootModel

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


class Volume(RootModel[AbsolutePath | DockerConfig | VolumeConfig]):
    def to_container_path(self) -> PosixPath:
        root = self.root
        if isinstance(root, PosixPath):
            return root
        else:
            return root.to_container_path()

    def to_args(self, volume_name: Input[str]) -> docker.ContainerVolumeArgs:
        root = self.root
        if isinstance(root, PosixPath):
            return docker.ContainerVolumeArgs(
                container_path=root.as_posix(), volume_name=volume_name
            )
        else:
            return root.to_args(volume_name)
