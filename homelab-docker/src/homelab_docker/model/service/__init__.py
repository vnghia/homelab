from functools import cached_property

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_vpn.config.service import ServiceVpnConfig
from pydantic import Field

from ...config.service.database import ServiceDatabaseConfig
from ...config.service.depend_on import ServiceDependOnConfig
from ...config.service.file import ServiceFileConfig
from ...config.service.keepass import ServiceKeepassConfig
from ...config.service.secret import ServiceSecretConfig
from ..docker.container import ContainerModel


class ServiceModel(HomelabBaseModel):
    depends_on: list[ServiceDependOnConfig] | None = None

    variables: dict[str, GlobalExtract] = {}
    databases: ServiceDatabaseConfig | None = None
    files: ServiceFileConfig | None = None
    secrets: ServiceSecretConfig | None = None
    keepasses: ServiceKeepassConfig | None = None
    vpn: ServiceVpnConfig | None = None
    container_: ContainerModel | None = Field(None, alias="container")
    containers_: dict[str, ContainerModel] = Field({}, alias="containers")

    @classmethod
    def add_service_name(cls, service_name: str, name: str | None) -> str:
        return "{}-{}".format(service_name, name) if name else service_name

    @cached_property
    def containers(self) -> dict[str | None, ContainerModel]:
        return ({None: self.container_} if self.container_ else {}) | self.containers_

    def __getitem__(self, key: str | None) -> ContainerModel:
        return self.containers[key]

    @property
    def vpn_(self) -> ServiceVpnConfig:
        if not self.vpn:
            raise ValueError("Service vpn config is not provided")
        return self.vpn


class ServiceWithConfigModel[T: HomelabBaseModel](ServiceModel):
    config: T
