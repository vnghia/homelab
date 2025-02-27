from __future__ import annotations

import typing
from typing import Never

import pulumi_random as random
from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from .....resource.service import ServiceResourceBase
    from ... import ContainerModel


class ContainerExtractSecretSource(HomelabBaseModel):
    secret: str

    def extract_str(
        self, _model: ContainerModel, main_service: ServiceResourceBase
    ) -> random.RandomPassword:
        return main_service.secret[self.secret]

    def extract_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> Never:
        raise TypeError("Can not extract path from secret source")

    def extract_volume_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> Never:
        raise TypeError("Can not extract volume path from secret source")
