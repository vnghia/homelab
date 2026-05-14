import functools
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

    @functools.cached_property
    def services(self) -> dict[str, ServiceModel]:
        from ...model.service import ServiceModel

        class AllowExtraServiceModel(ServiceModel):
            model_config = ConfigDict(extra="ignore")

        services = {
            name: service for name, service in self if isinstance(service, ServiceModel)
        }
        services |= self.extra(AllowExtraServiceModel)

        return services
