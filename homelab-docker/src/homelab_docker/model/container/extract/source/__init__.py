from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabRootModel

from ...volume_path import ContainerVolumePath
from .env import ContainerExtractEnvSource
from .simple import ContainerExtractSimpleSource
from .volume import ContainerExtractVolumeSource

if typing.TYPE_CHECKING:
    from ... import ContainerModel


class ContainerExtractSource(
    HomelabRootModel[
        ContainerExtractEnvSource
        | ContainerExtractVolumeSource
        | ContainerExtractSimpleSource
    ]
):
    def extract_str(self, model: ContainerModel) -> str:
        return self.root.extract_str(model)

    def extract_path(self, model: ContainerModel) -> AbsolutePath:
        return self.root.extract_path(model)

    def extract_volume_path(self, model: ContainerModel) -> ContainerVolumePath:
        return self.root.extract_volume_path(model)
