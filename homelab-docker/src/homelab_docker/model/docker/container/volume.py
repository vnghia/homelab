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
    ) -> docker.ContainerMountArgs:
        target = self.to_path(extractor_args).as_posix()

        if isinstance(volume, AbsolutePath):
            return docker.ContainerMountArgs(
                type="bind",
                target=target,
                read_only=self.read_only,
                source=volume.as_posix(),
            )
        return docker.ContainerMountArgs(
            type="volume",
            target=target,
            read_only=self.read_only,
            source=extractor_args.host.docker.volume.volumes[volume].name,
            volume_options=docker.ContainerMountVolumeOptionsArgs(no_copy=True),
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
    ) -> docker.ContainerMountArgs:
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
    ) -> list[docker.ContainerMountArgs]:
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
                    ContainerVolumeFullConfig(
                        path=GlobalExtract.from_simple("/var/run/docker.sock"),
                        read_only=not docker_socket_config.write,
                    ).to_args(
                        AbsolutePath(PosixPath("/var/run/docker.sock")), extractor_args
                    ),
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
                ContainerVolumeFullConfig(
                    path=GlobalExtract.from_simple(path),
                    read_only=True,
                ).to_args(AbsolutePath(PosixPath(path)), extractor_args)
                for path in ["/etc/localtime", "/usr/share/zoneinfo"]
            ]
        )

    def to_binds(
        self,
        docker_socket_config: ContainerDockerSocketConfig | None,
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs,
    ) -> list[Output[str]]:
        def to_bind(arg: docker.ContainerMountArgs) -> Output[str]:
            return Output.format(
                "{source}:{target}:{read_write}",
                source=arg.source,
                target=arg.target,
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
