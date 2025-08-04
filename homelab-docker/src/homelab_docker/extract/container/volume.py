from __future__ import annotations

import typing

from homelab_extract.container.volume import ContainerExtractVolumeSource
from homelab_pydantic import AbsolutePath

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.container.volume_path import ContainerVolumePath
    from .. import ExtractorArgs


class ContainerVolumeSourceExtractor(ExtractorBase[ContainerExtractVolumeSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        return self.extract_path(extractor_args).as_posix()

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return extractor_args.container.volumes[self.root.volume].to_path(
            extractor_args
        )

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        from ...model.container.volume_path import ContainerVolumePath

        return ContainerVolumePath(volume=self.root.volume)
