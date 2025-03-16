from __future__ import annotations

import typing
from typing import Never

from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalExtractVpnSource(HomelabBaseModel):
    port: str

    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        return Output.from_input(
            str(main_service.docker_resource_args.config.vpn.ports[self.port])
        )

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from vpn source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from vpn source")
