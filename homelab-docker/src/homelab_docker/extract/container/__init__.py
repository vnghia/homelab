from __future__ import annotations

import typing

from homelab_extract.container import ContainerExtract
from homelab_extract.container.env import ContainerExtractEnvSource
from homelab_extract.container.info import ContainerExtractInfoSource
from homelab_pydantic import AbsolutePath
from pulumi import Output

from .. import ExtractorBase
from .env import ContainerEnvSourceExtractor
from .info import ContainerInfoSourceExtractor
from .volume import ContainerVolumeSourceExtractor

if typing.TYPE_CHECKING:
    from ...model.docker.container.volume_path import ContainerVolumePath
    from .. import ExtractorArgs


class ContainerExtractor(ExtractorBase[ContainerExtract]):
    @property
    def extractor(
        self,
    ) -> (
        ContainerEnvSourceExtractor
        | ContainerInfoSourceExtractor
        | ContainerVolumeSourceExtractor
    ):
        root = self.root.root
        if isinstance(root, ContainerExtractEnvSource):
            return ContainerEnvSourceExtractor(root)
        if isinstance(root, ContainerExtractInfoSource):
            return ContainerInfoSourceExtractor(root)
        return ContainerVolumeSourceExtractor(root)

    def extract_str(self, extractor_args: ExtractorArgs) -> str | Output[str]:
        return self.extractor.extract_str(extractor_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.extractor.extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(extractor_args)
