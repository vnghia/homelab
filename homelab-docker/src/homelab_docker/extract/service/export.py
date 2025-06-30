from __future__ import annotations

import typing

from homelab_extract.service.export import ServiceExtractExportSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...resource.service import ServiceResourceBase


class ServiceExportSourceExtractor(ExtractorBase[ServiceExtractExportSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        root = self.root
        return main_service.exports[root.export]
