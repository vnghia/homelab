from __future__ import annotations

import typing
from typing import Never

import pulumi_random as random
from homelab_extract.service.secret import ServiceExtractSecretSource
from homelab_pydantic import HomelabRootModel

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...resource.service import ServiceResourceBase


class ServiceSecretSourceExtractor(HomelabRootModel[ServiceExtractSecretSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> random.RandomPassword:
        root = self.root
        return main_service.secret[root.secret]

    def extract_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract path from secret source")

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from secret source")
