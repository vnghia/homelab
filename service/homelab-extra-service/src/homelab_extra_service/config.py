from homelab_s3_config import S3ServiceConfigBase
from homelab_traefik_config import TraefikServiceConfigBase


class ExtraConfig(TraefikServiceConfigBase, S3ServiceConfigBase):
    pass
