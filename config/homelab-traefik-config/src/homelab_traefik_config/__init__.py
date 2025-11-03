from __future__ import annotations

from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict

from .model.dynamic import TraefikDynamicModel


class TraefikServiceDynamicConfig(HomelabServiceConfigDict[TraefikDynamicModel]):
    NONE_KEY = "traefik"


class TraefikServiceConfig(HomelabBaseModel):
    depends_on: list[str] = []
    dynamic: TraefikServiceDynamicConfig = TraefikServiceDynamicConfig({})


class TraefikServiceConfigBase(HomelabBaseModel):
    traefik: TraefikServiceConfig = TraefikServiceConfig()
