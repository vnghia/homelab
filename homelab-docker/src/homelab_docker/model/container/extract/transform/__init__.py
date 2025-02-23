from homelab_pydantic import AbsolutePath, HomelabBaseModel

from ...volume_path import ContainerVolumePath
from .path import ContainerExtractTransformPath
from .string import ContainerExtractTransformString


class ContainerExtractTransform(HomelabBaseModel):
    string: ContainerExtractTransformString = ContainerExtractTransformString()
    path: ContainerExtractTransformPath = ContainerExtractTransformPath()

    def transform_string(self, value: str) -> str:
        return self.string.transform(value)

    def transform_path(self, path: AbsolutePath) -> AbsolutePath:
        return self.path.transform(path)

    def transform_volume_path(
        self, volume_path: ContainerVolumePath
    ) -> ContainerVolumePath:
        return self.path.transform_volume_path(volume_path)
