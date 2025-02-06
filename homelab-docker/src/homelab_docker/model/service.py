from pydantic import BaseModel

from .container.model import ContainerModel
from .database import DatabaseModel


class ServiceModel[T](BaseModel):
    config: T
    databases: DatabaseModel | None = None
    container: ContainerModel
    containers: dict[str, ContainerModel] = {}
