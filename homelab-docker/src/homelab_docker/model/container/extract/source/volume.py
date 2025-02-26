from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel

from ...volume_path import ContainerVolumePath

if typing.TYPE_CHECKING:
    from .....resource.service import ServiceResourceBase
    from ... import ContainerModel


class ContainerExtractVolumeSource(HomelabBaseModel):
    volume: str

    def extract_str(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> str:
        return self.extract_path(model, main_service).as_posix()

    def extract_path(
        self, model: ContainerModel, _main_service: ServiceResourceBase
    ) -> AbsolutePath:
        return model.volumes[self.volume].to_path()

    def extract_volume_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return ContainerVolumePath(volume=self.volume)
