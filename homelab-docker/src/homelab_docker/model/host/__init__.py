from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_vpn import VpnConfig
from pydantic_extra_types.timezone_name import TimeZoneName

from ...config.docker import DockerConfig
from ...config.service import ServiceConfigBase
from ...config.service.database import ServiceDatabaseConfig
from ...model.host.ip import HostIpModel
from ...model.service import ServiceModel
from .access import HostAccessModel


class HostNoServiceModel(HomelabBaseModel):
    access: HostAccessModel
    timezone: TimeZoneName
    ip: HostIpModel = HostIpModel()
    vpn: VpnConfig | None = None
    docker: DockerConfig
    variables: dict[str, GlobalExtract] = {}

    @property
    def vpn_(self) -> VpnConfig:
        if not self.vpn:
            raise ValueError("VPN config is not provided")
        return self.vpn


class HostServiceModelModel(HostNoServiceModel):
    name: str
    services: dict[str, ServiceModel]

    @property
    def databases(self) -> dict[str, ServiceDatabaseConfig]:
        return {
            name: service.databases
            for name, service in self.services.items()
            if service.databases
        }


class HostModel[T: ServiceConfigBase](HostNoServiceModel):
    services: T

    def service_model(self, name: str) -> HostServiceModelModel:
        return HostServiceModelModel(
            name=name,
            services=self.services.services,
            **self.model_dump(exclude={"services"}),
        )
