from __future__ import annotations

import typing
from typing import Never

from homelab_extract.json import GlobalExtractJsonSource
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalJsonSourceExtractor(HomelabRootModel[GlobalExtractJsonSource]):
    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        from . import GlobalExtractor

        root = self.root
        return Output.json_dumps(
            GlobalExtractor.extract_recursively(root.json_, main_service, None)
        )

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from json source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from json source")
