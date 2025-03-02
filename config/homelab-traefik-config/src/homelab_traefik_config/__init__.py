from __future__ import annotations

from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict

from .model.dynamic import TraefikDynamicModel


class TraefikServiceConfig(HomelabServiceConfigDict[TraefikDynamicModel]):
    NONE_KEY = "traefik"


class TraefikServiceConfigBase(HomelabBaseModel):
    traefik: TraefikServiceConfig = TraefikServiceConfig({})
