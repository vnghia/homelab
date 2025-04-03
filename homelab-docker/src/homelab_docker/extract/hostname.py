from __future__ import annotations

import typing
from typing import Never

from homelab_extract.hostname import GlobalExtractHostnameSource
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalHostnameSourceExtractor(HomelabRootModel[GlobalExtractHostnameSource]):
    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        root = self.root
        hostname = main_service.docker_resource_args.hostnames[root.public][
            root.hostname
        ]
        if root.scheme:
            hostname = Output.format(
                "{}://{}{}", root.scheme, hostname, "/" if root.append_slash else ""
            )
        return hostname

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from hostname source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from hostname source")
