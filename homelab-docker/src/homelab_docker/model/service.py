from pydantic import BaseModel

from homelab_docker.model.container import Container


class Model(BaseModel):
    container: Container
    containers: dict[str, Container] = {}
