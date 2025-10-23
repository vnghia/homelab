from __future__ import annotations

import typing

from homelab_extract.container.volume import ContainerExtractVolumeSource
from homelab_extract.service.volume import ServiceExtractVolumeSource
from homelab_pydantic import AbsolutePath

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.docker.container.volume_path import ContainerVolumePath
    from .. import ExtractorArgs
    from ..container.volume import ContainerVolumeSourceExtractor


class ServiceVolumeSourceExtractor(ExtractorBase[ServiceExtractVolumeSource]):
    def to_container_extractor(self) -> ContainerVolumeSourceExtractor:
        from ..container.volume import ContainerVolumeSourceExtractor

        return ContainerVolumeSourceExtractor(
            ContainerExtractVolumeSource(volume=self.root.svolume)
        )

    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        if extractor_args._container:
            return self.to_container_extractor().extract_str(extractor_args)
        raise TypeError("Could not extract str from {}".format(self.name))

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        if extractor_args._container:
            return self.to_container_extractor().extract_path(extractor_args)
        raise TypeError("Could not extract path from {}".format(self.name))

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.to_container_extractor().extract_volume_path(extractor_args)
