from __future__ import annotations

import typing

import pulumi_random as random
from homelab_pydantic import AbsolutePath, HomelabRootModel
from pulumi import Output

from .env import ContainerExtractEnvSource
from .volume import ContainerExtractVolumeSource

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ContainerExtract(
    HomelabRootModel[ContainerExtractEnvSource | ContainerExtractVolumeSource]
):
    def extract_str(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> str | Output[str] | random.RandomPassword:
        return self.root.extract_str(model, main_service)

    def extract_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> AbsolutePath:
        return self.root.extract_path(model, main_service)

    def extract_volume_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(model, main_service)
