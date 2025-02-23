from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel

from ..volume_path import ContainerVolumePath
from .source import ContainerExtractSource
from .transform import ContainerExtractTransform

if typing.TYPE_CHECKING:
    from .. import ContainerModel


class ContainerExtract(HomelabBaseModel):
    source: ContainerExtractSource
    transform: ContainerExtractTransform = ContainerExtractTransform()

    def extract_str(self, model: ContainerModel) -> str:
        return self.transform.transform_string(self.source.extract_str(model))

    def extract_path(self, model: ContainerModel) -> AbsolutePath:
        return self.transform.transform_path(self.source.extract_path(model))

    def extract_volume_path(self, model: ContainerModel) -> ContainerVolumePath:
        return self.transform.transform_volume_path(
            self.source.extract_volume_path(model)
        )
