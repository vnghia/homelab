from homelab_pydantic import HomelabBaseModel
from homelab_traefik_service.config.service import TraefikServiceConfig


class DozzleConfig(HomelabBaseModel):
    traefik: TraefikServiceConfig
