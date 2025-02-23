from pathlib import PosixPath

from homelab_pydantic import AbsolutePath, HomelabBaseModel, RelativePath

from ...volume_path import ContainerVolumePath


class ContainerExtractTransformPath(HomelabBaseModel):
    child: RelativePath = RelativePath(PosixPath(""))

    def transform(self, path: AbsolutePath) -> AbsolutePath:
        return path / self.child

    def transform_volume_path(
        self, volume_path: ContainerVolumePath
    ) -> ContainerVolumePath:
        return volume_path / self.child
