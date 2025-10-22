from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract import GlobalExtract
from homelab_traefik_config import TraefikServiceConfigBase

from .state import KanidmStateConfig


class KandimConfig(TraefikServiceConfigBase, DaguServiceConfigBase):
    path: GlobalExtract
    port: GlobalExtract
    state: KanidmStateConfig
    address: GlobalExtract
