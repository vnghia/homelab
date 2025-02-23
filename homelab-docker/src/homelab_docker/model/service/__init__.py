from functools import cached_property

from homelab_pydantic import HomelabBaseModel
from pydantic import Field

from ...config.database import DatabaseConfig
from ..container import ContainerModel


class ServiceModel(HomelabBaseModel):
    databases: DatabaseConfig | None = None
    container_: ContainerModel | None = Field(None, alias="container")
    containers_: dict[str, ContainerModel] = Field({}, alias="containers")

    @cached_property
    def containers(self) -> dict[str | None, ContainerModel]:
        return self.containers_ | ({None: self.container_} if self.container_ else {})

    def __getitem__(self, key: str | None) -> ContainerModel:
        return self.containers[key]


class ServiceWithConfigModel[T: HomelabBaseModel](ServiceModel):
    config: T
