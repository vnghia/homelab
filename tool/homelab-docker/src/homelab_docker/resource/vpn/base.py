from __future__ import annotations

import typing

from homelab_pydantic import HomelabRootModel
from homelab_vpn.model.base import VpnBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class VpnBaseModelBuilder(HomelabRootModel[VpnBaseModel]):
    def build_envs(self, extractor_args: ExtractorArgs) -> dict[str, Output[str]]:
        from ...extract.global_ import GlobalExtractor

        root = self.root
        return {
            "FIREWALL_VPN_INPUT_PORTS": Output.from_input(
                ",".join(map(str, sorted(root.ports.root.values())))
            )
        } | {
            k: GlobalExtractor(v).extract_str(extractor_args)
            for k, v in root.envs.items()
        }
