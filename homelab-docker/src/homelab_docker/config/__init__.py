from homelab_pydantic import HomelabBaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from ..model.platform import Platform
from .image import ImageConfig
from .network import NetworkConfig
from .plugin import PluginConfig
from .service import ServiceConfigBase
from .volume import VolumeConfig


class DockerConfig[T: ServiceConfigBase](HomelabBaseModel):
    platform: Platform
    timezone: TimeZoneName
    network: NetworkConfig
    images: ImageConfig
    plugins: PluginConfig
    volumes: VolumeConfig
    services: T
