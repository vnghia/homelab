from __future__ import annotations

import typing

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pulumi import Input, Output

from homelab_docker.extract import GlobalExtractor
from homelab_docker.model.container.docker_socket import ContainerDockerSocketConfig

if typing.TYPE_CHECKING:
    from ...resource.service import ServiceResourceBase
    from . import ContainerModel, ContainerModelBuildArgs


class ContainerVolumeFullConfig(HomelabBaseModel):
    path: GlobalExtract
    read_only: bool = False

    def to_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return GlobalExtractor(self.path).extract_path(main_service, model)

    def to_args(
        self,
        volume_name: Input[str],
        main_service: ServiceResourceBase,
        model: ContainerModel | None,
    ) -> docker.ContainerVolumeArgs:
        return docker.ContainerVolumeArgs(
            container_path=self.to_path(main_service, model).as_posix(),
            read_only=self.read_only,
            volume_name=volume_name,
        )


class ContainerVolumeConfig(
    HomelabRootModel[GlobalExtract | ContainerVolumeFullConfig]
):
    def to_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        root = self.root
        if isinstance(root, GlobalExtract):
            return GlobalExtractor(root).extract_path(main_service, model)
        return root.to_path(main_service, model)

    def to_args(
        self,
        volume_name: Input[str],
        main_service: ServiceResourceBase,
        model: ContainerModel | None,
    ) -> docker.ContainerVolumeArgs:
        root = self.root
        if isinstance(root, GlobalExtract):
            return docker.ContainerVolumeArgs(
                container_path=GlobalExtractor(root)
                .extract_path(main_service, model)
                .as_posix(),
                volume_name=volume_name,
            )
        return root.to_args(volume_name, main_service, model)


class ContainerVolumesConfig(HomelabRootModel[dict[str, ContainerVolumeConfig]]):
    root: dict[str, ContainerVolumeConfig] = {}

    def __getitem__(self, key: str) -> ContainerVolumeConfig:
        return self.root[key]

    def to_args(
        self,
        docker_socket_config: ContainerDockerSocketConfig | None,
        main_service: ServiceResourceBase,
        model: ContainerModel | None,
        build_args: ContainerModelBuildArgs,
    ) -> list[docker.ContainerVolumeArgs]:
        volume_resource = main_service.docker_resource_args.volume
        return (
            (
                [
                    volume.to_args(
                        volume_name=volume_resource[name].name,
                        main_service=main_service,
                        model=model,
                    )
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
                    volume.to_args(
                        volume_name=volume_resource[name].name,
                        main_service=main_service,
                        model=model,
                    )
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
        main_service: ServiceResourceBase,
        model: ContainerModel | None,
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
            for arg in self.to_args(
                docker_socket_config, main_service, model, build_args
            )
        ]
