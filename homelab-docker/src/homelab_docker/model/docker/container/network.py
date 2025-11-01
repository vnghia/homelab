from __future__ import annotations

import dataclasses
import typing
from enum import StrEnum, auto

import pulumi_docker as docker
from homelab_extract import GlobalExtract
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
from ....model.docker.network import BridgeNetworkModel

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


@dataclasses.dataclass
class ContainerNetworkArgs:
    mode: Input[str]
    advanced: list[docker.ContainerNetworksAdvancedArgs]


class NetworkMode(StrEnum):
    HOST = auto()


class ContainerNetworkContainerConfig(HomelabBaseModel):
    service: str | None = None
    container: str | None = None

    def to_args(
        self, _resource_name: str | None, extractor_args: ExtractorArgs
    ) -> ContainerNetworkArgs:
        return ContainerNetworkArgs(
            mode=Output.format(
                "container:{0}",
                GlobalExtractor(
                    GlobalExtract(
                        HostExtract(
                            HostExtractFull(
                                service=self.service,
                                extract=ServiceExtract(
                                    ServiceExtractFull(
                                        container=self.container,
                                        extract=ContainerExtract(
                                            ContainerExtractInfoSource(
                                                cinfo=ContainerInfoSource.ID
                                            )
                                        ),
                                    ),
                                ),
                            )
                        )
                    )
                ).extract_str(extractor_args),
            ),
            advanced=[],
        )


class ContainerNetworkModeConfig(HomelabBaseModel):
    mode: NetworkMode

    def to_args(
        self, resource_name: str | None, extractor_args: ExtractorArgs
    ) -> ContainerNetworkArgs:
        match self.mode:
            case NetworkMode.HOST:
                return ContainerNetworkArgs(mode="host", advanced=[])


class ContainerBridgeNetworkConfig(HomelabBaseModel):
    active: bool = True
    aliases: list[GlobalExtract] = []


class ContainerCommonNetworkConfig(HomelabBaseModel):
    bridge: dict[str, ContainerBridgeNetworkConfig] = {}

    def build_resource_aliases(
        self,
        resource_name: str | None,
        bridge_model: BridgeNetworkModel,
        bridge_config: ContainerBridgeNetworkConfig,
        extractor_args: ExtractorArgs,
    ) -> list[Input[str]]:
        if bridge_model.icc:
            resource_aliases: list[Input[str]] = []
            if resource_name:
                resource_aliases.append(resource_name)
            resource_aliases += [
                GlobalExtractor(alias).extract_str(extractor_args)
                for alias in bridge_config.aliases
            ]
            return resource_aliases
        return []

    def to_args(
        self, resource_name: str | None, extractor_args: ExtractorArgs
    ) -> ContainerNetworkArgs:
        # TODO: remove bridge mode after https://github.com/pulumi/pulumi-docker/issues/1272
        bridge_config = extractor_args.host.docker.network.config.bridge
        return ContainerNetworkArgs(
            mode="bridge",
            advanced=[
                extractor_args.host.docker.network.get_bridge_args(
                    name,
                    self.build_resource_aliases(
                        resource_name, bridge_config[name], config, extractor_args
                    ),
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
