from __future__ import annotations

import typing

from homelab_pydantic import HomelabRootModel
from homelab_vpn.model import VpnModel
from pulumi import Output

from .wireguard import VpnWireguardModelBuilder

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class VpnModelBuilder(HomelabRootModel[VpnModel]):
    def build_envs(self, extractor_args: ExtractorArgs) -> dict[str, Output[str]]:
        root = self.root.root
        return VpnWireguardModelBuilder(root).build_envs(extractor_args)
