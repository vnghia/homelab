from __future__ import annotations

import typing

from homelab_extract.container.volume import ContainerExtractVolumeSource
from homelab_pydantic import AbsolutePath

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ContainerVolumeSourceExtractor(ExtractorBase[ContainerExtractVolumeSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str:
        model = self.ensure_valid_model(model)
        return self.extract_path(main_service, model).as_posix()

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        root = self.root
        model = self.ensure_valid_model(model)
        return model.volumes[root.volume].to_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        from ...model.container.volume_path import ContainerVolumePath

        root = self.root
        return ContainerVolumePath(volume=root.volume)
