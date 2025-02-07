from pydantic import BaseModel

from homelab_docker.config.database import DatabaseConfig

from .container.model import ContainerModel


class ServiceModel[T](BaseModel):
    config: T
    databases: DatabaseConfig = DatabaseConfig()
    container: ContainerModel
    containers: dict[str, ContainerModel] = {}
