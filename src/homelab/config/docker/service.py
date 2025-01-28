import homelab_docker as docker
from pydantic import BaseModel


class Service(BaseModel):
    container: docker.container.Container
    containers: dict[str, docker.container.Container] = {}
