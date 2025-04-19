from __future__ import annotations

import typing
from typing import Never

from homelab_extract.hostname import GlobalExtractHostnameSource
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalHostnameSourceExtractor(HomelabRootModel[GlobalExtractHostnameSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Output[str]:
        return self.root.to_hostname(main_service.docker_resource_args.hostnames)

    def extract_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract path from hostname source")

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from hostname source")
