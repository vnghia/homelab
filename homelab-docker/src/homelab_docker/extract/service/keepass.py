from __future__ import annotations

import typing
from enum import StrEnum, auto
from typing import Never

from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...resource.service import ServiceResourceBase


class KeepassInfoSource(StrEnum):
    USERNAME = auto()
    PASSWORD = auto()


class ServiceExtractKeepassSource(HomelabBaseModel):
    keepass: str | None
    info: KeepassInfoSource

    def extract_str(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Output[str]:
        entry = main_service.keepass[self.keepass]
        match self.info:
            case KeepassInfoSource.USERNAME:
                return entry.username
            case KeepassInfoSource.PASSWORD:
                return entry.password

    def extract_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract path from keepass source")

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from keepass source")
