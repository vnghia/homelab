from __future__ import annotations

import typing

from homelab_extract.kv import GlobalExtractKvSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalKvSourceExtractor(ExtractorBase[GlobalExtractKvSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> dict[str, Output[str]]:
        from .global_ import GlobalExtractor

        root = self.root
        return {
            key: GlobalExtractor(value).extract_str(main_service, model)
            for key, value in root.kv.items()
        }
