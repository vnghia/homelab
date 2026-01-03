from homelab_dagu_config import DaguServiceConfigBase
from homelab_traefik_config import TraefikServiceConfigBase


class ExtraConfig(TraefikServiceConfigBase, DaguServiceConfigBase):
    pass
