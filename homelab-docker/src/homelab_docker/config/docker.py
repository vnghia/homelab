from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from homelab_docker.config.image import Image
from homelab_docker.config.network import Network
from homelab_docker.config.volume import Volume


class Docker[T: BaseModel](BaseModel):
    timezone: TimeZoneName
    network: Network
    images: Image
    volumes: Volume
    services: T
