from pydantic import BaseModel

from homelab_docker.config.image import Image
from homelab_docker.config.network import Network
from homelab_docker.config.volume import Volume


class Docker(BaseModel):
    network: Network
    images: Image
    volume: Volume
