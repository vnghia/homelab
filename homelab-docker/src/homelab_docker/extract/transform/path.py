from __future__ import annotations

import typing

from homelab_extract.transform.path import ExtractTransformPath
from homelab_pydantic import AbsolutePath
from homelab_pydantic.model import HomelabRootModel

if typing.TYPE_CHECKING:
    from ...model.container.volume_path import ContainerVolumePath


class ExtractPathTransformer(HomelabRootModel[ExtractTransformPath]):
    def transform(self, path: AbsolutePath) -> AbsolutePath:
        root = self.root.root
        return path / root

    def transform_volume_path(
        self, volume_path: ContainerVolumePath
    ) -> ContainerVolumePath:
        root = self.root.root
        return volume_path / root
