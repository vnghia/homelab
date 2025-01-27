import homelab_docker as docker
from pydantic import BaseModel


class Service(BaseModel):
    containers: dict[str, docker.container.Container]
