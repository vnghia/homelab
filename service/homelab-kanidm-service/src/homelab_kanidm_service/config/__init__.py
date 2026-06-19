from homelab_extract import GlobalExtract
from homelab_traefik_config import TraefikServiceConfigBase

from .state import KanidmStateConfig


class KandimConfig(TraefikServiceConfigBase):
    path: GlobalExtract
    port: GlobalExtract
    state: KanidmStateConfig
    address: GlobalExtract
    record: str
