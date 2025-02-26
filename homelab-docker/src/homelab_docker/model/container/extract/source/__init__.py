from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabRootModel

from ...volume_path import ContainerVolumePath
from .env import ContainerExtractEnvSource
from .global_ import ContainerExtractGlobalSource
from .simple import ContainerExtractSimpleSource
from .volume import ContainerExtractVolumeSource

if typing.TYPE_CHECKING:
    from .....resource.service import ServiceResourceBase
    from ... import ContainerModel


class ContainerExtractSource(
    HomelabRootModel[
        ContainerExtractGlobalSource
        | ContainerExtractEnvSource
        | ContainerExtractVolumeSource
        | ContainerExtractSimpleSource
    ]
):
    def extract_str(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> str:
        return self.root.extract_str(model, main_service)

    def extract_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> AbsolutePath:
        return self.root.extract_path(model, main_service)

    def extract_volume_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(model, main_service)
