from homelab_pydantic import HomelabBaseModel

from .middleware import TraefikDynamicMiddlewareModel
from .service import TraefikDynamicServiceModel


class TraefikDynamicBaseModel(HomelabBaseModel):
    active: bool = True

    entrypoint: str | None = None
    keep_default_middleware: bool = True

    name: str | None = None
    record: str | None = None

    service: TraefikDynamicServiceModel
    middlewares: list[TraefikDynamicMiddlewareModel] = []
