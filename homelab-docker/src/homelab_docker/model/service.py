from pydantic import BaseModel

from .container.model import ContainerModel
from .database import DatabaseModel


class ServiceModel[T](BaseModel):
    config: T
    databases: DatabaseModel = DatabaseModel()
    container: ContainerModel
    containers: dict[str, ContainerModel] = {}
