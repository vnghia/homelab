import typing
from pathlib import PosixPath

import pulumi_docker as docker
from pulumi import Input, Output
from pydantic import BaseModel, ConfigDict, Field, RootModel

from homelab_docker.pydantic import AbsolutePath

if typing.TYPE_CHECKING:
    from ...resource.volume import VolumeResource


class ContainerVolumeFullConfig(BaseModel):
    path: AbsolutePath
    read_only: bool = Field(False, alias="read-only")

    def to_container_path(self) -> PosixPath:
        return self.path

    def to_args(self, volume_name: Input[str]) -> docker.ContainerVolumeArgs:
        return docker.ContainerVolumeArgs(
            container_path=self.to_container_path().as_posix(),
            read_only=self.read_only,
            volume_name=volume_name,
        )


class ContainerVolumeConfig(RootModel[AbsolutePath | ContainerVolumeFullConfig]):
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


class ContainerVolumesConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    docker_socket: bool | None = Field(None, alias="docker-socket")
    __pydantic_extra__: dict[str, ContainerVolumeConfig] = Field({}, init=False)  # pyright: ignore [reportIncompatibleVariableOverride]

    def __getitem__(self, key: str) -> ContainerVolumeConfig:
        return self.__pydantic_extra__[key]

    def to_args(
        self, volume_resource: "VolumeResource"
    ) -> list[docker.ContainerVolumeArgs]:
        return (
            (
                [
                    volume.to_args(volume_name=volume_resource[name].name)
                    for name, volume in self.__pydantic_extra__.items()
                ]
                if self.__pydantic_extra__
                else []
            )
            + (
                [
                    docker.ContainerVolumeArgs(
                        container_path="/var/run/docker.sock",
                        host_path="/var/run/docker.sock",
                        read_only=not self.docker_socket,
                    )
                ]
                if self.docker_socket is not None
                else []
            )
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

    def to_binds(self, volume_resource: "VolumeResource") -> list[Output[str]]:
        def to_bind(arg: docker.ContainerVolumeArgs) -> Output[str]:
            return Output.format(
                "{volume_or_path}:{container_path}:{read_write}",
                volume_or_path=arg.volume_name if arg.volume_name else arg.host_path,
                container_path=arg.container_path,
                read_write=(
                    Output.from_input(arg.read_only).apply(
                        lambda x: "ro" if x else "rw"
                    )
                )
                if arg.read_only is not None
                else "rw",
            )

        return [to_bind(arg) for arg in self.to_args(volume_resource)]
