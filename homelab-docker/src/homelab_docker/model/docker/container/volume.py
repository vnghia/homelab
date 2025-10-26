from __future__ import annotations

import typing
from functools import cached_property
from pathlib import PosixPath

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pulumi import Output
from pydantic import ValidationError

from ....extract.global_ import GlobalExtractor
from .docker_socket import ContainerDockerSocketConfig

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs
    from . import ContainerModelBuildArgs


class ContainerVolumeFullConfig(HomelabBaseModel):
    active: bool = True
    path: GlobalExtract
    read_only: bool = False

    def to_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return GlobalExtractor(self.path).extract_path(extractor_args)

    def to_args(
        self, volume: AbsolutePath | str, extractor_args: ExtractorArgs
    ) -> docker.ContainerVolumeArgs:
        host_path = None
        volume_name = None
        if isinstance(volume, AbsolutePath):
            host_path = volume.as_posix()
        else:
            volume_resource = extractor_args.host.docker.volume
            volume_name = volume_resource.volumes[volume].name

        return docker.ContainerVolumeArgs(
            container_path=self.to_path(extractor_args).as_posix(),
            host_path=host_path,
            read_only=self.read_only,
            volume_name=volume_name,
        )


class ContainerVolumeConfig(
    HomelabRootModel[GlobalExtract | ContainerVolumeFullConfig]
):
    @property
    def active(self) -> bool:
        root = self.root
        if isinstance(root, ContainerVolumeFullConfig):
            return root.active
        return True

    def to_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        root = self.root
        if isinstance(root, GlobalExtract):
            return GlobalExtractor(root).extract_path(extractor_args)
        return root.to_path(extractor_args)

    def to_args(
        self, volume: AbsolutePath | str, extractor_args: ExtractorArgs
    ) -> docker.ContainerVolumeArgs:
        root = self.root
        if isinstance(root, GlobalExtract):
            root = ContainerVolumeFullConfig(path=root)
        return root.to_args(volume, extractor_args)


class ContainerVolumesConfig(HomelabRootModel[dict[str, ContainerVolumeConfig]]):
    root: dict[str, ContainerVolumeConfig] = {}

    def __getitem__(self, key: str) -> ContainerVolumeConfig:
        return self.root[key]

    @cached_property
    def volumes(self) -> dict[str | AbsolutePath, ContainerVolumeConfig]:
        volumes = {}
        for key, config in self.root.items():
            if not config.active:
                continue
            try:
                volume: AbsolutePath | str = AbsolutePath(PosixPath(key))
            except ValidationError:
                volume = key
            volumes[volume] = config
        return volumes

    def to_args(
        self,
        docker_socket_config: ContainerDockerSocketConfig | None,
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs,
    ) -> list[docker.ContainerVolumeArgs]:
        volumes = self.volumes
        return (
            (
                [
                    volume.to_args(volume=name, extractor_args=extractor_args)
                    for name, volume in volumes.items()
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
                    volume.to_args(volume=name, extractor_args=extractor_args)
                    for name, volume in sorted(
                        build_args.volumes.items(), key=lambda x: x[0]
                    )
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
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs,
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
            for arg in self.to_args(docker_socket_config, extractor_args, build_args)
        ]
