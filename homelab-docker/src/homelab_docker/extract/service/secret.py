from __future__ import annotations

import typing

from homelab_extract.service.secret import ServiceExtractSecretSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...resource.service import ServiceResourceBase


class ServiceSecretSourceExtractor(ExtractorBase[ServiceExtractSecretSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        root = self.root
        return main_service.secret[root.secret].result
