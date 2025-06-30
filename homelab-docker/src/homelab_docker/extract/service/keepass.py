from __future__ import annotations

import typing

from homelab_extract.service.keepass import (
    KeepassInfoSource,
    ServiceExtractKeepassSource,
)
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...resource.service import ServiceResourceBase


class ServiceKeepassSourceExtractor(ExtractorBase[ServiceExtractKeepassSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        root = self.root
        entry = main_service.keepass[root.keepass]
        match root.info:
            case KeepassInfoSource.USERNAME:
                return entry.username
            case KeepassInfoSource.PASSWORD:
                return entry.password
