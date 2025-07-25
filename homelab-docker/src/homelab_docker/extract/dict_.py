from __future__ import annotations

import typing
from typing import Any

from homelab_extract.dict_ import GlobalExtractDictSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalDictSourceExtractor(ExtractorBase[GlobalExtractDictSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> dict[Output[str], Any]:
        from .global_ import GlobalExtractor

        root = self.root
        return {
            GlobalExtractor(key).extract_str(
                main_service, model
            ): GlobalExtractor.extract_recursively(value, main_service, model)
            for [key, value] in root.dict_
        }
