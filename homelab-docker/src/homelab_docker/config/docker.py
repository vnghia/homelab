from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from homelab_docker.model.platform import Platform

from .image import ImageConfig
from .network import NetworkConfig
from .plugin import PluginConfig
from .service import ServiceConfigBase
from .volume import VolumeConfig


class DockerConfig[T: ServiceConfigBase](BaseModel):
    platform: Platform
    timezone: TimeZoneName
    network: NetworkConfig
    images: ImageConfig
    plugins: PluginConfig
    volumes: VolumeConfig
    services: T
