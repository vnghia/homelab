from __future__ import annotations

import typing
from typing import Never

from homelab_extract.service.export import ServiceExtractExportSource
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...resource.service import ServiceResourceBase


class ServiceExportSourceExtractor(HomelabRootModel[ServiceExtractExportSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Output[str]:
        root = self.root
        return main_service.exports[root.export]

    def extract_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract path from export source")

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from export source")
