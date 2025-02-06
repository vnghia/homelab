from pydantic import BaseModel

from .container.model import ContainerModel


class ServiceModel[T](BaseModel):
    config: T
    container: ContainerModel
    containers: dict[str, ContainerModel] = {}
