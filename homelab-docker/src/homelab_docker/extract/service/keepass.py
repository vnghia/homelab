from __future__ import annotations

import typing
from typing import Never

from homelab_extract.service.keepass import (
    KeepassInfoSource,
    ServiceExtractKeepassSource,
)
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...resource.service import ServiceResourceBase


class ServiceKeepassSourceExtractor(HomelabRootModel[ServiceExtractKeepassSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Output[str]:
        root = self.root
        entry = main_service.keepass[root.keepass]
        match root.info:
            case KeepassInfoSource.USERNAME:
                return entry.username
            case KeepassInfoSource.PASSWORD:
                return entry.password

    def extract_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract path from keepass source")

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from keepass source")
