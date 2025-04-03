from __future__ import annotations

import typing
from typing import Never

from homelab_extract.id import GlobalExtractIdSource
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalIdSourceExtractor(HomelabRootModel[GlobalExtractIdSource]):
    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        root = self.root
        return main_service.containers[root.id].id

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from container id source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from container id source")
