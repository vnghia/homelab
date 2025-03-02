from __future__ import annotations

import typing

import pulumi_random as random
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase
    from . import ContainerExtract


class ContainerExtractEnvSource(HomelabBaseModel):
    env: str

    def get_env(self, model: ContainerModel) -> ContainerExtract:
        return model.envs[self.env]

    def extract_str(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> str | Output[str] | random.RandomPassword:
        return self.get_env(model).extract_str(model, main_service)

    def extract_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> AbsolutePath:
        return self.get_env(model).extract_path(model, main_service)

    def extract_volume_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.get_env(model).extract_volume_path(model, main_service)
