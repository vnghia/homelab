import typing
from pathlib import PosixPath

import pulumi_docker as docker
from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pulumi import Input, Output

from homelab_docker.model.container.docker_socket import ContainerDockerSocketConfig

if typing.TYPE_CHECKING:
    from ...resource import DockerResourceArgs
    from . import ContainerModelBuildArgs


class ContainerVolumeFullConfig(HomelabBaseModel):
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


class ContainerVolumeConfig(HomelabRootModel[AbsolutePath | ContainerVolumeFullConfig]):
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


class ContainerVolumesConfig(HomelabRootModel[dict[str, ContainerVolumeConfig]]):
    root: dict[str, ContainerVolumeConfig] = {}

    def __getitem__(self, key: str) -> ContainerVolumeConfig:
        return self.root[key]

    def to_args(
        self,
        docker_socket_config: ContainerDockerSocketConfig | None,
        build_args: "ContainerModelBuildArgs",
        docker_resource_args: "DockerResourceArgs",
    ) -> list[docker.ContainerVolumeArgs]:
        volume_resource = docker_resource_args.volume
        return (
            (
                [
                    volume.to_args(volume_name=volume_resource[name].name)
                    for name, volume in self.root.items()
                ]
            )
            + (
                [
                    docker.ContainerVolumeArgs(
                        container_path="/var/run/docker.sock",
                        host_path="/var/run/docker.sock",
                        read_only=not docker_socket_config.write,
                    )
                ]
                if docker_socket_config
                else []
            )
            + (
                [
                    volume.to_args(volume_name=volume_resource[name].name)
                    for name, volume in build_args.volumes.items()
                ]
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

    def to_binds(
        self,
        docker_socket_config: ContainerDockerSocketConfig | None,
        build_args: "ContainerModelBuildArgs",
        docker_resource_args: "DockerResourceArgs",
    ) -> list[Output[str]]:
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

        return [
            to_bind(arg)
            for arg in self.to_args(
                docker_socket_config, build_args, docker_resource_args
            )
        ]
