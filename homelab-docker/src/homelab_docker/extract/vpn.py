from __future__ import annotations

import typing
from typing import Never

from homelab_extract.vpn import GlobalExtractVpnSource
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalVpnSourceExtractor(HomelabRootModel[GlobalExtractVpnSource]):
    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        root = self.root
        return Output.from_input(
            str(main_service.docker_resource_args.config.vpn.ports[root.port])
        )

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from vpn source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from vpn source")
