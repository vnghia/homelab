from __future__ import annotations

import typing

import pulumi_random as random
from homelab_extract.container import ContainerExtract
from homelab_extract.container.env import ContainerExtractEnvSource
from homelab_pydantic import AbsolutePath, HomelabRootModel
from pulumi import Output

from .env import ContainerEnvSourceExtractor
from .volume import ContainerVolumeSourceExtractor

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ContainerExtractor(HomelabRootModel[ContainerExtract]):
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
    ) -> str | Output[str] | random.RandomPassword:
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
