from homelab_pydantic import HomelabBaseModel

from .middleware import TraefikDynamicMiddlewareModel
from .service import TraefikDynamicServiceModel


class TraefikDynamicTcpModel(HomelabBaseModel):
    active: bool = True
    name: str | None = None
    record: str
    hostsni: str

    service: TraefikDynamicServiceModel
    middlewares: list[TraefikDynamicMiddlewareModel] = []
