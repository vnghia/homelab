from pathlib import PosixPath

import pulumi_docker as docker
from pulumi import Input
from pydantic import BaseModel, ConfigDict, RootModel

from homelab_docker.pydantic import AbsolutePath
from homelab_docker.resource.volume import Volume as VolumeResource


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


class Volume(RootModel[AbsolutePath | VolumeConfig]):
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


class Volumes(BaseModel):
    model_config = ConfigDict(extra="allow")

    docker_socket: bool | None = None
    __pydantic_extra__: dict[str, Volume] = {}  # pyright: ignore [reportIncompatibleVariableOverride]

    def __getitem__(self, key: str) -> Volume:
        if not self.__pydantic_extra__:
            raise ValueError("volumes config is empty")
        return self.__pydantic_extra__[key]

    def to_args(
        self, volume_resource: VolumeResource
    ) -> list[docker.ContainerVolumeArgs]:
        return (
            [
                volume.to_args(volume_name=volume_resource[name].name)
                for name, volume in self.__pydantic_extra__.items()
            ]
            if self.__pydantic_extra__
            else []
            + [
                docker.ContainerVolumeArgs(
                    container_path="/var/run/docker.sock",
                    host_path="/var/run/docker.sock",
                    read_only=self.docker_socket,
                )
            ]
            if self.docker_socket is not None
            else []
            + [
                docker.ContainerVolumeArgs(
                    container_path="/etc/localtime",
                    host_path="/etc/localtime",
                    read_only=True,
                ),
                docker.ContainerVolumeArgs(
                    container_path="/usr/share/zoneinfo",
                    host_path="/usr/share/zoneinfo",
                    read_only=True,
                ),
            ]
        )
