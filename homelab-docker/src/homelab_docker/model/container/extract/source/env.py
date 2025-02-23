from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel

from ...volume_path import ContainerVolumePath

if typing.TYPE_CHECKING:
    from ... import ContainerModel
    from ...extract import ContainerExtract


class ContainerExtractEnvSource(HomelabBaseModel):
    env: str

    def get_env(self, model: ContainerModel) -> ContainerExtract:
        return model.envs[self.env]

    def extract_str(self, model: ContainerModel) -> str:
        return self.get_env(model).extract_str(model)

    def extract_path(self, model: ContainerModel) -> AbsolutePath:
        return self.get_env(model).extract_path(model)

    def extract_volume_path(self, model: ContainerModel) -> ContainerVolumePath:
        return self.get_env(model).extract_volume_path(model)
