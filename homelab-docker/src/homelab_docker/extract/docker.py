from __future__ import annotations

import typing

from homelab_extract.docker import GlobalExtractDockerSource

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalDockerSourceExtractor(ExtractorBase[GlobalExtractDockerSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str:
        root = self.root
        return root.docker.format(
            timezone=main_service.docker_resource_args.timezone,
            **{
                k.removeprefix("pulumi."): v
                for k, v in main_service.docker_resource_args.project_labels.items()
            },
        )
