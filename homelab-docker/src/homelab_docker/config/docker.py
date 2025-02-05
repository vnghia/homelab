from typing import Generic, TypeVar

from pydantic import BaseModel

from homelab_docker.config.image import Image
from homelab_docker.config.network import Network
from homelab_docker.config.volume import Volume

Service = TypeVar("Service", bound=BaseModel)


class Docker(BaseModel, Generic[Service]):
    network: Network
    images: Image
    volumes: Volume
    services: Service
