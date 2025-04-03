from __future__ import annotations

import typing
from typing import Never

from homelab_extract.docker import GlobalExtractDockerSource
from homelab_pydantic import HomelabRootModel

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalDockerSourceExtractor(HomelabRootModel[GlobalExtractDockerSource]):
    def extract_str(self, main_service: ServiceResourceBase) -> str:
        root = self.root
        return root.docker.format(
            timezone=main_service.docker_resource_args.timezone,
            **{
                k.removeprefix("pulumi."): v
                for k, v in main_service.docker_resource_args.project_labels.items()
            },
        )

    def extract_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract path from global source")

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from global source")
