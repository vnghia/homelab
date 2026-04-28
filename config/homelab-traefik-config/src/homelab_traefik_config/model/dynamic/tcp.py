from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

from .base import TraefikDynamicBaseModel


class TraefikDynamicTcpTlsModel(HomelabBaseModel):
    enabled: bool = True
    passthrough: bool = True


class TraefikDynamicTcpModel(TraefikDynamicBaseModel):
    hostsni: str | list[GlobalExtract] | None
    tls: TraefikDynamicTcpTlsModel = TraefikDynamicTcpTlsModel()
