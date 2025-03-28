from __future__ import annotations

import typing
from typing import Any, Never

from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalExtractJsonSource(HomelabBaseModel):
    json: Any

    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        from . import GlobalExtract

        return Output.json_dumps(
            GlobalExtract.extract_recursively(self.json, main_service, None)
        )

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from json source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from json source")
