from __future__ import annotations

import typing

from homelab_pydantic import HomelabRootModel
from homelab_vpn.model.wireguard import VpnWireguardModel
from pulumi import Output

from .base import VpnBaseModelBuilder

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class VpnWireguardModelBuilder(HomelabRootModel[VpnWireguardModel]):
    def build_envs(self, extractor_args: ExtractorArgs) -> dict[str, Output[str]]:
        from ...extract.global_ import GlobalExtractor

        root = self.root
        return VpnBaseModelBuilder(root.to_parent()).build_envs(extractor_args) | {
            "WIREGUARD_PRIVATE_KEY": GlobalExtractor(root.private_key).extract_str(
                extractor_args
            ),
            "WIREGUARD_PRESHARED_KEY": GlobalExtractor(root.preshared_key).extract_str(
                extractor_args
            ),
            "WIREGUARD_ADDRESSES": Output.all(
                *[
                    GlobalExtractor(address).extract_str(extractor_args)
                    for address in root.addresses
                ]
            ).apply(lambda x: ",".join(x)),
            "VPN_TYPE": Output.from_input("wireguard"),
        }
