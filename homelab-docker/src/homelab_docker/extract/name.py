from __future__ import annotations

import typing

from homelab_extract.name import GlobalExtractNameSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalNameSourceExtractor(ExtractorBase[GlobalExtractNameSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        root = self.root
        return main_service.containers[root.name].name
