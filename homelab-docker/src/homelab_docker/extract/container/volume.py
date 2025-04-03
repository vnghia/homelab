from __future__ import annotations

import typing

from homelab_extract.container.volume import ContainerExtractVolumeSource
from homelab_pydantic import AbsolutePath, HomelabRootModel

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ContainerVolumeSourceExtractor(HomelabRootModel[ContainerExtractVolumeSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel
    ) -> str:
        return self.extract_path(main_service, model).as_posix()

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel
    ) -> AbsolutePath:
        root = self.root
        return model.volumes[root.volume].to_path(main_service, model)

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel
    ) -> ContainerVolumePath:
        from ...model.container.volume_path import ContainerVolumePath

        root = self.root
        return ContainerVolumePath(volume=root.volume)
