from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from ..config.database import DatabaseConfig
    from ..model.service import ServiceModel


class ServiceConfigBase(HomelabBaseModel):
    @property
    def services(self) -> dict[str, ServiceModel]:
        from ..model.service import ServiceModel

        return {
            name: service for name, service in self if isinstance(service, ServiceModel)
        }

    @property
    def databases(self) -> dict[str, DatabaseConfig]:
        return {
            name: service.databases
            for name, service in self.services.items()
            if service.databases
        }
