from __future__ import annotations

import typing

from homelab_extract.json import GlobalExtractJsonSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalJsonSourceExtractor(ExtractorBase[GlobalExtractJsonSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        from .global_ import GlobalExtractor

        root = self.root
        return Output.json_dumps(
            GlobalExtractor.extract_recursively(root.json_, main_service, model)
        )
