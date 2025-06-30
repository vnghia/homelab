from __future__ import annotations

import typing

from homelab_extract.container import ContainerExtract
from homelab_extract.container.env import ContainerExtractEnvSource
from homelab_pydantic import AbsolutePath
from pulumi import Output

from .. import ExtractorBase
from .env import ContainerEnvSourceExtractor
from .volume import ContainerVolumeSourceExtractor

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ContainerExtractor(ExtractorBase[ContainerExtract]):
    @property
    def extractor(
        self,
    ) -> ContainerEnvSourceExtractor | ContainerVolumeSourceExtractor:
        root = self.root.root
        return (
            ContainerEnvSourceExtractor(root)
            if isinstance(root, ContainerExtractEnvSource)
            else ContainerVolumeSourceExtractor(root)
        )

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str]:
        return self.extractor.extract_str(
            main_service, model or main_service.model[None]
        )

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.extractor.extract_path(
            main_service, model or main_service.model[None]
        )

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(
            main_service, model or main_service.model[None]
        )
