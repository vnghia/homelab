from __future__ import annotations

import typing

from homelab_extract.hostname import GlobalExtractHostnameSource

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalHostnameSourceExtractor(ExtractorBase[GlobalExtractHostnameSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str:
        return self.root.to_hostname(main_service.docker_resource_args.hostnames)
