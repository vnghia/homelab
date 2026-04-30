from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import HomelabBaseModel
from pydantic import ConfigDict

if typing.TYPE_CHECKING:
    from ...model.service import ServiceModel


class ServiceConfigBase(HomelabBaseModel):
    model_config = ConfigDict(extra="allow")

    _services: dict[str, ServiceModel]

    def model_post_init(self, context: Any, /) -> None:
        from ...model.service import ServiceModel

        class AllowExtraServiceModel(ServiceModel):
            model_config = ConfigDict(extra="ignore")

        self._services = {
            name: service for name, service in self if isinstance(service, ServiceModel)
        }
        self._services |= self.extra(AllowExtraServiceModel)

    def extra[T: ServiceModel](self, model_type_: type[T]) -> dict[str, T]:
        return {
            name: model_type_.model_validate(data)
            for name, data in (self.model_extra or {}).items()
        }

    @property
    def services(self) -> dict[str, ServiceModel]:
        return self._services
