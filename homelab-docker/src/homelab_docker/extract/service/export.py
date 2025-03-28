from __future__ import annotations

import typing
from typing import Never

from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...resource.service import ServiceResourceBase


class ServiceExtractExportSource(HomelabBaseModel):
    export: str

    def extract_str(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Output[str]:
        return main_service.exports[self.export]

    def extract_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract path from export source")

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from export source")
