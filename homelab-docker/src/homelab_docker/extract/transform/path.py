from __future__ import annotations

import typing
from pathlib import PosixPath

from homelab_pydantic import AbsolutePath, RelativePath
from homelab_pydantic.model import HomelabRootModel

if typing.TYPE_CHECKING:
    from ...model.container.volume_path import ContainerVolumePath


class ExtractTransformPath(HomelabRootModel[RelativePath]):
    root: RelativePath = RelativePath(PosixPath(""))

    def transform(self, path: AbsolutePath) -> AbsolutePath:
        return path / self.root

    def transform_volume_path(
        self, volume_path: ContainerVolumePath
    ) -> ContainerVolumePath:
        return volume_path / self.root
