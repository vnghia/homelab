from homelab_mail import MailConfig
from homelab_pydantic import HomelabBaseModel
from homelab_s3 import S3Config
from homelab_vpn import VpnConfig
from pydantic_extra_types.timezone_name import TimeZoneName

from ..model.platform import Platform
from .database import DatabaseConfig
from .host import HostConfig
from .image import ImageConfig
from .network import NetworkConfig
from .plugin import PluginConfig
from .service import ServiceConfigBase
from .volume import VolumeConfig


class DockerNoServiceConfig(HomelabBaseModel):
    host: HostConfig
    platform: Platform
    timezone: TimeZoneName
    network: NetworkConfig
    vpn: VpnConfig
    images: ImageConfig
    database: DatabaseConfig
    plugins: PluginConfig
    volumes: VolumeConfig
    s3: S3Config = S3Config({})
    mail: MailConfig = MailConfig({})


class DockerConfig[T: ServiceConfigBase](DockerNoServiceConfig):
    services: T
