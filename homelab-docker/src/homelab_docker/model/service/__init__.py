from functools import cached_property

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import Field

from ...config.service.database import ServiceDatabaseConfig
from ...config.service.file import ServiceFileConfig
from ...config.service.keepass import ServiceKeepassConfig
from ...config.service.secret import ServiceSecretConfig
from ..docker.container import ContainerModel


class ServiceModel(HomelabBaseModel):
    variables: dict[str, GlobalExtract] = {}
    databases: ServiceDatabaseConfig | None = None
    files: ServiceFileConfig | None = None
    secrets: ServiceSecretConfig | None = None
    keepasses: ServiceKeepassConfig | None = None
    container_: ContainerModel | None = Field(None, alias="container")
    containers_: dict[str, ContainerModel] = Field({}, alias="containers")

    @cached_property
    def containers(self) -> dict[str | None, ContainerModel]:
        return ({None: self.container_} if self.container_ else {}) | self.containers_

    def __getitem__(self, key: str | None) -> ContainerModel:
        return self.containers[key]


class ServiceWithConfigModel[T: HomelabBaseModel](ServiceModel):
    config: T
