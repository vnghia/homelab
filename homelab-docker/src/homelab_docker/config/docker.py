from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from .image import ImageConfig
from .network import NetworkConfig
from .service import ServiceConfigBase
from .volume import VolumeConfig


class DockerConfig[T: ServiceConfigBase](BaseModel):
    timezone: TimeZoneName
    network: NetworkConfig
    images: ImageConfig
    volumes: VolumeConfig
    services: T
