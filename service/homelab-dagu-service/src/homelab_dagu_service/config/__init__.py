from homelab_docker.model.service.extract import ServiceExtract
from homelab_pydantic import HomelabBaseModel
from homelab_traefik_service.config.dynamic.http import TraefikDynamicHttpConfig


class DaguConfig(HomelabBaseModel):
    dags_dir: ServiceExtract
    log_dir: ServiceExtract
    traefik: TraefikDynamicHttpConfig
