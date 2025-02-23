from homelab_pydantic import HomelabBaseModel
from pydantic import Field

from ..config.database import DatabaseConfig
from .container import ContainerModel


class ServiceModel(HomelabBaseModel):
    databases: DatabaseConfig | None = None
    raw_container: ContainerModel | None = Field(None, alias="container")
    containers: dict[str, ContainerModel] = {}

    @property
    def container(self) -> ContainerModel:
        if self.raw_container is None:
            raise ValueError("Service main container model is None")
        return self.raw_container


class ServiceWithConfigModel[T: HomelabBaseModel](ServiceModel):
    config: T
