import homelab_docker as docker
from pydantic import BaseModel


class Network(BaseModel):
    bridge: dict[str, docker.network.Bridge]
