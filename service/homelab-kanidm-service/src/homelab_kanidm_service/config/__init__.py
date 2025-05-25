from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract import GlobalExtract
from homelab_pydantic.model import HomelabBaseModel
from homelab_traefik_config import TraefikServiceConfigBase

from .state import KanidmStateConfig


class KanidmPathConfig(HomelabBaseModel):
    config: GlobalExtract
    tls_key: GlobalExtract
    tls_chain: GlobalExtract
    db: GlobalExtract


class KandimConfig(TraefikServiceConfigBase, DaguServiceConfigBase):
    path: KanidmPathConfig
    port: GlobalExtract
    domain: GlobalExtract
    origin: GlobalExtract
    state: KanidmStateConfig
