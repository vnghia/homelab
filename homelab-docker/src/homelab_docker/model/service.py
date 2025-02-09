from pydantic import BaseModel, Field

from homelab_docker.config.database import DatabaseConfig

from .build.model import BuildModel
from .container.model import ContainerModel


class ServiceModel[T](BaseModel):
    raw_config: T | None = Field(None, alias="config")
    builds: dict[str, BuildModel] = {}
    databases: DatabaseConfig = DatabaseConfig()
    raw_container: ContainerModel | None = Field(None, alias="container")
    containers: dict[str, ContainerModel] = {}

    @property
    def config(self) -> T:
        if self.raw_config is None:
            raise ValueError("Service config is None")
        return self.raw_config

    @property
    def container(self) -> ContainerModel:
        if self.raw_container is None:
            raise ValueError("Service main container model is None")
        return self.raw_container
