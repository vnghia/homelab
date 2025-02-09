from pydantic import BaseModel

from homelab_docker.config.database import DatabaseConfig

from .build.model import BuildModel
from .container.model import ContainerModel


class ServiceModel[T](BaseModel):
    config: T
    builds: dict[str, BuildModel] = {}
    databases: DatabaseConfig = DatabaseConfig()
    container: ContainerModel
    containers: dict[str, ContainerModel] = {}
