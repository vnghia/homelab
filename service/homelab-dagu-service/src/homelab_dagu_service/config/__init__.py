from homelab_docker.model.service.extract import ServiceExtract
from homelab_traefik_config import TraefikServiceConfigBase


class DaguConfig(TraefikServiceConfigBase):
    dags_dir: ServiceExtract
    log_dir: ServiceExtract
