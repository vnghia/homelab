from __future__ import annotations

import typing

from homelab_extract.host import GlobalExtractHostSource, HostInfoSource

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalHostSourceExtractor(ExtractorBase[GlobalExtractHostSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str:
        root = self.root
        host = main_service.docker_resource_args.config.host
        match root.host:
            case HostInfoSource.USER:
                return host.user
            case HostInfoSource.ADDRESS:
                return host.address
