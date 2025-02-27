from __future__ import annotations

import typing
from typing import Never

from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from .....resource.service import ServiceResourceBase
    from ... import ContainerModel


class ContainerExtractHostnameSource(HomelabBaseModel):
    hostname: str
    public: bool

    def extract_str(
        self, _model: ContainerModel, main_service: ServiceResourceBase
    ) -> Output[str]:
        return main_service.docker_resource_args.hostnames[self.public][self.hostname]

    def extract_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> Never:
        raise TypeError("Can not extract path from hostname source")

    def extract_volume_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> Never:
        raise TypeError("Can not extract volume path from hostname source")
