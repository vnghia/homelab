from __future__ import annotations

import typing

import pulumi_random as random
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase
    from .. import GlobalExtract


class ContainerExtractEnvSource(HomelabBaseModel):
    env: str

    def get_env(self, model: ContainerModel) -> GlobalExtract:
        return model.envs[self.env]

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel
    ) -> str | Output[str] | random.RandomPassword:
        return self.get_env(model).extract_str(main_service, model)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel
    ) -> AbsolutePath:
        return self.get_env(model).extract_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel
    ) -> ContainerVolumePath:
        return self.get_env(model).extract_volume_path(main_service, model)
