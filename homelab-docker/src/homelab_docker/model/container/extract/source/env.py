from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel

from ...volume_path import ContainerVolumePath

if typing.TYPE_CHECKING:
    from .....resource.service import ServiceResourceBase
    from ... import ContainerModel
    from ...extract import ContainerExtract


class ContainerExtractEnvSource(HomelabBaseModel):
    env: str

    def get_env(self, model: ContainerModel) -> ContainerExtract:
        return model.envs[self.env]

    def extract_str(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> str:
        return self.get_env(model).extract_str(model, main_service)

    def extract_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> AbsolutePath:
        return self.get_env(model).extract_path(model, main_service)

    def extract_volume_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.get_env(model).extract_volume_path(model, main_service)
