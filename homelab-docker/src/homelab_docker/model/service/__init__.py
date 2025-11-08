from typing import Any

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import Field

from ...config.service.database import ServiceDatabaseConfig
from ...config.service.depend_on import ServiceDependOnConfig
from ...config.service.file import ServiceFileConfig
from ...config.service.keepass import ServiceKeepassConfig
from ...config.service.move import ServiceMoveConfig
from ...config.service.network import ServiceNetworkConfig
from ...config.service.secret import ServiceSecretConfig
from ..docker.container import ContainerModel


class ServiceModel(HomelabBaseModel):
    old: ServiceMoveConfig | None = None
    depends_on: list[ServiceDependOnConfig] | None = None

    variables: dict[str, GlobalExtract] = {}
    databases: ServiceDatabaseConfig | None = None
    files: ServiceFileConfig | None = None
    secrets: ServiceSecretConfig | None = None
    keepasses: ServiceKeepassConfig | None = None
    network: ServiceNetworkConfig = ServiceNetworkConfig()
    container_: ContainerModel | None = Field(None, alias="container")
    containers_: dict[str, ContainerModel] = Field({}, alias="containers")

    _containers: dict[str | None, ContainerModel]

    def model_post_init(self, context: Any, /) -> None:
        self._containers = (
            {None: self.container_} if self.container_ else {}
        ) | self.containers_

    @classmethod
    def add_service_name(cls, service_name: str, name: str | None) -> str:
        return "{}-{}".format(service_name, name) if name else service_name

    @property
    def containers(self) -> dict[str | None, ContainerModel]:
        return self._containers

    def __getitem__(self, key: str | None) -> ContainerModel:
        return self.containers[key]


class ServiceWithConfigModel[T: HomelabBaseModel](ServiceModel):
    config: T
