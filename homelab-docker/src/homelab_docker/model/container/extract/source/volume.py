from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel

from ...volume_path import ContainerVolumePath

if typing.TYPE_CHECKING:
    from ... import ContainerModel


class ContainerExtractVolumeSource(HomelabBaseModel):
    volume: str

    def extract_str(self, model: ContainerModel) -> str:
        return self.extract_path(model).as_posix()

    def extract_path(self, model: ContainerModel) -> AbsolutePath:
        return model.volumes[self.volume].to_container_path()

    def extract_volume_path(self, _model: ContainerModel) -> ContainerVolumePath:
        return ContainerVolumePath(volume=self.volume)
