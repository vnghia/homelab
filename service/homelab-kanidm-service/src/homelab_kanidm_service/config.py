from homelab_docker.extract import GlobalExtract
from homelab_traefik_config import TraefikServiceConfigBase


class KandimConfig(TraefikServiceConfigBase):
    tls_key: GlobalExtract
    tls_chain: GlobalExtract
