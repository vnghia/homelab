from homelab_extract import GlobalExtract

from .base import TraefikDynamicBaseModel
from .tls import TraefikDynamicTlsModel


class TraefikDynamicHttpModel(TraefikDynamicBaseModel):
    hostname: str | None = None
    prefix: GlobalExtract | None = None

    rules: list[GlobalExtract] = []
    tls: TraefikDynamicTlsModel | None = None
