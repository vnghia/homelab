from pydantic import BaseModel

from homelab_docker.model.container import Model as ContainerModel


class Model[T](BaseModel):
    config: T
    container: ContainerModel
    containers: dict[str, ContainerModel] = {}
