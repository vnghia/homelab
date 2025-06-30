from __future__ import annotations

import typing

import pulumi_random as random
from homelab_extract.container.env import ContainerExtractEnvSource
from homelab_pydantic import AbsolutePath
from homelab_pydantic.model import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase
    from ..global_ import GlobalExtractor


class ContainerEnvSourceExtractor(HomelabRootModel[ContainerExtractEnvSource]):
    def get_env(self, model: ContainerModel) -> GlobalExtractor:
        from ..global_ import GlobalExtractor

        root = self.root
        return GlobalExtractor(model.envs[root.env])

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
