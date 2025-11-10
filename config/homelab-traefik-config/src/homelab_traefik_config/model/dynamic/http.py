from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

from .middleware import TraefikDynamicMiddlewareModel
from .service import TraefikDynamicServiceModel
from .tls import TraefikDynamicTlsModel


class TraefikDynamicHttpModel(HomelabBaseModel):
    active: bool = True
    name: str | None = None
    record: str | None = None
    hostname: str | None = None
    prefix: GlobalExtract | None = None

    rules: list[GlobalExtract] = []
    service: TraefikDynamicServiceModel
    middlewares: list[TraefikDynamicMiddlewareModel] = []
    tls: TraefikDynamicTlsModel | None = None
