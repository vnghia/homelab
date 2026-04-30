from homelab_pydantic import HomelabBaseModel

from ...model.docker.platform import Platform
from .database import DatabaseConfig
from .image import ImageConfig
from .network import NetworkConfig
from .plugin import PluginConfig
from .volume import VolumeConfig


class DockerConfig(HomelabBaseModel):
    platform: Platform
    network: NetworkConfig
    images: ImageConfig = ImageConfig()
    database: DatabaseConfig = DatabaseConfig()
    plugins: PluginConfig = PluginConfig()
    volumes: VolumeConfig = VolumeConfig()
