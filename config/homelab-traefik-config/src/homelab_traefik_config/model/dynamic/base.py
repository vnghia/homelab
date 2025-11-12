from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

from .middleware import TraefikDynamicMiddlewareModel
from .service import TraefikDynamicServiceModel


class TraefikDynamicBaseModel(HomelabBaseModel):
    active: bool = True

    address: GlobalExtract | None = None
    entrypoint: str | None = None

    name: str | None = None
    record: str | None = None

    service: TraefikDynamicServiceModel
    middlewares: list[TraefikDynamicMiddlewareModel] = []
