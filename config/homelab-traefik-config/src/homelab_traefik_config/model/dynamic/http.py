from __future__ import annotations

from homelab_docker.extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

from .middleware import TraefikDynamicMiddlewareModel
from .service import TraefikDynamicServiceModel


class TraefikDynamicHttpModel(HomelabBaseModel):
    name: str | None = None
    public: bool
    hostname: str | None = None
    prefix: GlobalExtract | None = None

    rules: list[GlobalExtract] = []
    service: TraefikDynamicServiceModel
    middlewares: list[TraefikDynamicMiddlewareModel] = []
