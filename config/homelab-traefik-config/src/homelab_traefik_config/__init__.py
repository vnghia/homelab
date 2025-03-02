from __future__ import annotations

from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict

from .model.dynamic.http import TraefikDynamicHttpModel
from .model.dynamic.middleware import TraefikDynamicMiddlewareFullModel


class TraefikServiceConfig(
    HomelabServiceConfigDict[
        TraefikDynamicHttpModel | TraefikDynamicMiddlewareFullModel
    ]
):
    NONE_KEY = "traefik"


class TraefikServiceConfigBase(HomelabBaseModel):
    traefik: TraefikServiceConfig
