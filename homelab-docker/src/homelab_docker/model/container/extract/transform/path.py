from pathlib import PosixPath

from homelab_pydantic import AbsolutePath, RelativePath
from homelab_pydantic.model import HomelabRootModel

from ...volume_path import ContainerVolumePath


class ContainerExtractTransformPath(HomelabRootModel[RelativePath]):
    root: RelativePath = RelativePath(PosixPath(""))

    def transform(self, path: AbsolutePath) -> AbsolutePath:
        return path / self.root

    def transform_volume_path(
        self, volume_path: ContainerVolumePath
    ) -> ContainerVolumePath:
        return volume_path / self.root
