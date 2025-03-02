from __future__ import annotations

import typing
from typing import Never

from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from ...resource.service import ServiceResourceBase


class ServiceExtractVariableSource(HomelabBaseModel):
    variable: str

    def extract_str(self, main_service: ServiceResourceBase) -> str:
        return main_service.model.variables[self.variable].extract_str(main_service)

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from variable source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from variable source")
