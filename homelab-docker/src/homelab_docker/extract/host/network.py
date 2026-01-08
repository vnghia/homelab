from __future__ import annotations

import typing

from homelab_extract.host.network import HostExtractNetworkSource, HostNetworkInfoSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class HostNetworkSourceExtractor(ExtractorBase[HostExtractNetworkSource]):
    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> list[Output[str]] | Output[str]:
        network = self.root.network
        info = self.root.info
        network_resource = extractor_args.host.docker.network
        match info:
            case HostNetworkInfoSource.SUBNET:
                return network_resource.service_subnets[network]
            case HostNetworkInfoSource.PROXY4:
                if ipv4 := network_resource.proxy_option.bridges[network].ipv4:
                    return ipv4
                raise ValueError(
                    "Proxy static ipv4 is not available for this network {}".format(
                        network
                    )
                )
            case HostNetworkInfoSource.PROXY6:
                if ipv6 := network_resource.proxy_option.bridges[network].ipv6:
                    return ipv6
                raise ValueError(
                    "Proxy static ipv6 is not available for this network {}".format(
                        network
                    )
                )
