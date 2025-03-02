from __future__ import annotations

from homelab_docker.model.service.extract import ServiceExtract
from homelab_pydantic import HomelabBaseModel

from .middleware import TraefikDynamicMiddlewareModel
from .service import TraefikDynamicServiceModel


class TraefikDynamicHttpModel(HomelabBaseModel):
    name: str | None = None
    public: bool
    hostname: str | None = None
    prefix: ServiceExtract | None = None

    rules: list[ServiceExtract] = []
    service: TraefikDynamicServiceModel
    middlewares: list[TraefikDynamicMiddlewareModel] = []
