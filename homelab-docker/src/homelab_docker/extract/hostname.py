from __future__ import annotations

import typing
from typing import Never

from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalExtractHostnameSource(HomelabBaseModel):
    hostname: str
    public: bool

    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        return main_service.docker_resource_args.hostnames[self.public][self.hostname]

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from hostname source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from hostname source")
