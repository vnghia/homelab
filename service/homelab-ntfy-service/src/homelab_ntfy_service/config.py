from homelab_pydantic import HomelabBaseModel
from homelab_traefik_service.config.service import TraefikServiceConfig


class NtfyConfig(HomelabBaseModel):
    traefik: TraefikServiceConfig = TraefikServiceConfig({})
