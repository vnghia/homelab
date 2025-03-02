from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ContainerExtractVolumeSource(HomelabBaseModel):
    volume: str

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel
    ) -> str:
        return self.extract_path(main_service, model).as_posix()

    def extract_path(
        self, _main_service: ServiceResourceBase, model: ContainerModel
    ) -> AbsolutePath:
        return model.volumes[self.volume].to_path()

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel
    ) -> ContainerVolumePath:
        from ...model.container.volume_path import ContainerVolumePath

        return ContainerVolumePath(volume=self.volume)
