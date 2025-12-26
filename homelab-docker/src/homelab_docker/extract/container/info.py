from __future__ import annotations

import typing

from homelab_extract.container.info import (
    ContainerExtractInfoSource,
    ContainerInfoSource,
)
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ContainerInfoSourceExtractor(ExtractorBase[ContainerExtractInfoSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str | Output[str]:
        cinfo = self.root.cinfo
        match cinfo:
            case ContainerInfoSource.ID:
                return extractor_args.container.id
            case ContainerInfoSource.NAME:
                return extractor_args.container.name
            case ContainerInfoSource.DNS:
                from ...model.docker.container.host import ContainerHostModeConfig
                from ...model.docker.container.network import (
                    ContainerNetworkContainerConfig,
                    ContainerNetworkModeConfig,
                    NetworkMode,
                )
                from ...model.host import HostNoServiceModel

                network = extractor_args.container_model.network.root
                if isinstance(network, ContainerNetworkContainerConfig):
                    extractor_args.get_service(network.service).containers[
                        network.container
                    ]
                    return HostNoServiceModel.add_prefix(
                        network.service or extractor_args.service.name(),
                        network.container,
                    )
                if isinstance(network, ContainerNetworkModeConfig):
                    match network.mode:
                        case NetworkMode.HOST:
                            return ContainerHostModeConfig.LOCALHOST_IP
                return extractor_args.service.add_service_name(
                    extractor_args.container.key
                )
