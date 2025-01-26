from homelab_docker.image import Platform
from pydantic import BaseModel


class Server(BaseModel):
    platform: Platform
