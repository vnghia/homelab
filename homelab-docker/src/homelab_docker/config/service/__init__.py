from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel
from pydantic import ConfigDict

if typing.TYPE_CHECKING:
    from ...model.service import ServiceModel


class ServiceConfigBase(HomelabBaseModel):
    model_config = ConfigDict(extra="allow")

    def extra[T: ServiceModel](self, model_type_: type[T]) -> dict[str, T]:
        return {
            name: model_type_.model_validate(data)
            for name, data in (self.model_extra or {}).items()
        }

    @property
    def services(self) -> dict[str, ServiceModel]:
        from ...model.service import ServiceModel

        class AllowExtraServiceModel(ServiceModel):
            model_config = ConfigDict(extra="ignore")

        results: typing.Mapping[str, ServiceModel] = {
            name: AllowExtraServiceModel.model_validate(service.model_dump())
            for name, service in self
            if isinstance(service, ServiceModel)
        } | self.extra(AllowExtraServiceModel)

        return dict(results)
