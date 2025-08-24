from __future__ import annotations

import dataclasses
import typing
from enum import StrEnum, auto

import pulumi_docker as docker
from homelab_extract import GlobalExtract, GlobalExtractFull
from homelab_extract.container import ContainerExtract
from homelab_extract.container.info import (
    ContainerExtractInfoSource,
    ContainerInfoSource,
)
from homelab_extract.host import HostExtract, HostExtractFull
from homelab_extract.service import ServiceExtract, ServiceExtractFull
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Input, Output

from ....extract.global_ import GlobalExtractor

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


@dataclasses.dataclass
class ContainerNetworkArgs:
    mode: Input[str]
    advanced: list[docker.ContainerNetworksAdvancedArgs]


class NetworkMode(StrEnum):
    HOST = auto()
    VPN = auto()


class ContainerNetworkContainerConfig(HomelabBaseModel):
    container: GlobalExtract

    def to_args(
        self, _resource_name: str | None, extractor_args: ExtractorArgs
    ) -> ContainerNetworkArgs:
        return ContainerNetworkArgs(
            mode=Output.format(
                "container:{0}",
                GlobalExtractor(self.container).extract_str(extractor_args),
            ),
            advanced=[],
        )


class ContainerNetworkModeConfig(HomelabBaseModel):
    mode: NetworkMode

    def to_args(
        self, resource_name: str | None, extractor_args: ExtractorArgs
    ) -> ContainerNetworkArgs:
        match self.mode:
            case NetworkMode.VPN:
                vpn_config = extractor_args.host_model.vpn_
                return ContainerNetworkContainerConfig(
                    container=GlobalExtract(
                        GlobalExtractFull(
                            extract=HostExtract(
                                HostExtractFull(
                                    service=vpn_config.service,
                                    extract=ServiceExtract(
                                        ServiceExtractFull(
                                            container=vpn_config.container,
                                            extract=ContainerExtract(
                                                ContainerExtractInfoSource(
                                                    cinfo=ContainerInfoSource.ID
                                                )
                                            ),
                                        ),
                                    ),
                                )
                            ),
                        )
                    )
                ).to_args(resource_name, extractor_args)
            case NetworkMode.HOST:
                return ContainerNetworkArgs(mode="host", advanced=[])


class ContainerBridgeNetworkConfig(HomelabBaseModel):
    active: bool = True
    aliases: list[GlobalExtract] = []


class ContainerCommonNetworkConfig(HomelabBaseModel):
    bridge: dict[str, ContainerBridgeNetworkConfig] = {}

    def to_args(
        self, resource_name: str | None, extractor_args: ExtractorArgs
    ) -> ContainerNetworkArgs:
        # TODO: remove bridge mode after https://github.com/pulumi/pulumi-docker/issues/1272
        resource_aliases = [resource_name] if resource_name else []
        return ContainerNetworkArgs(
            mode="bridge",
            advanced=[
                extractor_args.host.docker.network.get_bridge_args(
                    name,
                    [
                        *resource_aliases,
                        *[
                            GlobalExtractor(alias).extract_str(extractor_args)
                            for alias in config.aliases
                        ],
                    ],
                )
                for name, config in self.bridge.items()
                if config.active
            ],
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
        self, resource_name: str | None, extractor_args: ExtractorArgs
    ) -> ContainerNetworkArgs:
        default = extractor_args.host_model.docker.network.default.root
        root = self.root
        if type(default) is type(root):
            return default.model_merge(root).to_args(resource_name, extractor_args)  # type: ignore
        return root.to_args(resource_name, extractor_args)
