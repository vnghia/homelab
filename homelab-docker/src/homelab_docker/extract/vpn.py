from __future__ import annotations

import typing

from homelab_extract.vpn import GlobalExtractVpnSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalVpnSourceExtractor(ExtractorBase[GlobalExtractVpnSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        root = self.root
        return Output.from_input(
            str(main_service.docker_resource_args.config.vpn_.ports[root.port])
        )
