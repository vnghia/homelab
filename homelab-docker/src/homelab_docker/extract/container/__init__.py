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
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str] | random.RandomPassword:
        return self.root.extract_str(main_service, model or main_service.model[None])

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.root.extract_path(main_service, model or main_service.model[None])

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(
            main_service, model or main_service.model[None]
        )
