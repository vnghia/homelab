from __future__ import annotations

import typing
from typing import Never

from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalExtractIdSource(HomelabBaseModel):
    id: str | None

    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        return main_service.containers[self.id].id

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from container id source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from container id source")
