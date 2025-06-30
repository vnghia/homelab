from __future__ import annotations

import typing

from homelab_extract.container.env import ContainerExtractEnvSource
from homelab_pydantic import AbsolutePath
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase
    from ..global_ import GlobalExtractor


class ContainerEnvSourceExtractor(ExtractorBase[ContainerExtractEnvSource]):
    def get_env(self, model: ContainerModel | None) -> GlobalExtractor:
        from ..global_ import GlobalExtractor

        root = self.root
        model = self.ensure_valid_model(model)
        return GlobalExtractor(model.envs[root.env])

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str]:
        return self.get_env(model).extract_str(main_service, model)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.get_env(model).extract_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.get_env(model).extract_volume_path(main_service, model)
