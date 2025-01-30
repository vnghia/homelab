from typing import Generic, TypeVar

import homelab_docker as docker
from pydantic import BaseModel

Config = TypeVar("Config")


class Service(BaseModel, Generic[Config]):
    container: docker.container.Container
    containers: dict[str, docker.container.Container] = {}
    config: Config | None = None
