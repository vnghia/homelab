from __future__ import annotations

import typing

from homelab_extract.service.variable import ServiceExtractVariableSource
from homelab_pydantic import AbsolutePath
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase
    from ..global_ import GlobalExtractor


class ServiceVariableSourceExtractor(ExtractorBase[ServiceExtractVariableSource]):
    def get_variable(self, main_service: ServiceResourceBase) -> GlobalExtractor:
        from ..global_ import GlobalExtractor

        root = self.root
        return GlobalExtractor(main_service.model.variables[root.variable])

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str]:
        return self.get_variable(main_service).extract_str(main_service, model)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.get_variable(main_service).extract_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.get_variable(main_service).extract_volume_path(main_service, model)
