from __future__ import annotations

import typing

from homelab_extract.host.network import HostExtractNetworkSource, HostNetworkInfoSource
from pulumi import Output
from pydantic import IPvAnyNetwork

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class HostNetworkSourceExtractor(ExtractorBase[HostExtractNetworkSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> list[Output[IPvAnyNetwork]]:
        info = self.root.info
        match info:
            case HostNetworkInfoSource.SUBNET:
                return extractor_args.host.docker.network.service_subnets[
                    self.root.network
                ]
