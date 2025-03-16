from __future__ import annotations

import dataclasses
import typing
from enum import StrEnum, auto

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Input, Output

from homelab_docker.extract import GlobalExtract, GlobalExtractFull, GlobalExtractSource
from homelab_docker.extract.id import GlobalExtractIdSource

if typing.TYPE_CHECKING:
    from ...resource.service import ServiceResourceBase


@dataclasses.dataclass
class ContainerNetworkArgs:
    mode: Input[str]
    advanced: list[docker.ContainerNetworksAdvancedArgs]


class NetworkMode(StrEnum):
    VPN = auto()


class ContainerNetworkContainerConfig(HomelabBaseModel):
    container: GlobalExtract

    def to_args(
        self, _resource_name: str | None, main_service: ServiceResourceBase
    ) -> ContainerNetworkArgs:
        return ContainerNetworkArgs(
            mode=Output.format(
                "container:{0}", self.container.extract_str(main_service, None)
            ),
            advanced=[],
        )


class ContainerNetworkModeConfig(HomelabBaseModel):
    mode: NetworkMode

    def to_args(
        self, resource_name: str | None, main_service: ServiceResourceBase
    ) -> ContainerNetworkArgs:
        match self.mode:
            case NetworkMode.VPN:
                vpn_config = main_service.docker_resource_args.config.vpn
                return ContainerNetworkContainerConfig(
                    container=GlobalExtract(
                        GlobalExtractFull(
                            service=vpn_config.service,
                            extract=GlobalExtractSource(
                                GlobalExtractIdSource(id=vpn_config.container)
                            ),
                        )
                    )
                ).to_args(resource_name, main_service)


class ContainerCommonNetworkConfig(HomelabBaseModel):
    default_bridge: bool = False
    internal_bridge: bool = True

    def to_args(
        self, resource_name: str | None, main_service: ServiceResourceBase
    ) -> ContainerNetworkArgs:
        # TODO: remove bridge mode after https://github.com/pulumi/pulumi-docker/issues/1272
        aliases = [resource_name] if resource_name else []
        return ContainerNetworkArgs(
            mode="bridge",
            advanced=(
                [main_service.docker_resource_args.network.default_bridge_args(aliases)]
                if self.default_bridge
                else []
            )
            + (
                [
                    main_service.docker_resource_args.network.internal_bridge_args(
                        aliases
                    )
                ]
                if self.internal_bridge
                else []
            ),
        )


class ContainerNetworkConfig(
    HomelabRootModel[
        ContainerCommonNetworkConfig
        | ContainerNetworkContainerConfig
        | ContainerNetworkModeConfig
    ]
):
    root: (
        ContainerCommonNetworkConfig
        | ContainerNetworkContainerConfig
        | ContainerNetworkModeConfig
    ) = ContainerCommonNetworkConfig()

    def to_args(
        self, resource_name: str | None, main_service: ServiceResourceBase
    ) -> ContainerNetworkArgs:
        return self.root.to_args(resource_name, main_service)
