from functools import cached_property

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import ConfigDict
from pydantic_extra_types.timezone_name import TimeZoneName

from ...config.docker import DockerConfig
from ...config.service import ServiceConfigBase
from ...config.service.database import ServiceDatabaseConfig
from ...model.host.ip import HostIpModel
from ...model.service import ServiceModel
from .access import HostAccessModel


class HostNoServiceModel(HomelabBaseModel):
    byname: str
    access: HostAccessModel
    timezone: TimeZoneName
    ip: HostIpModel
    docker: DockerConfig
    variables: dict[str, GlobalExtract] = {}


class HostServiceModelModel(HostNoServiceModel):
    model_config = ConfigDict(revalidate_instances="never")

    name: str
    services: dict[str, ServiceModel]

    @cached_property
    def databases(self) -> dict[str, ServiceDatabaseConfig]:
        return {
            name: service.databases
            for name, service in self.services.items()
            if service.databases
        }


class HostModel[T: ServiceConfigBase](HostNoServiceModel):
    services: T

    def service_model(self, name: str) -> HostServiceModelModel:
        model = dict(self)
        model["services"] = self.services.services
        return HostServiceModelModel.model_construct(name=name, **model)
