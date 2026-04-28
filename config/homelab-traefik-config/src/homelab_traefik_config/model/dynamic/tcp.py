from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from .base import TraefikDynamicBaseModel


class TraefikDynamicTcpTlsModel(HomelabBaseModel):
    enabled: bool = True
    passthrough: bool = True


class TraefikDynamicTcpProxyProtocolModel(HomelabBaseModel):
    enabled: bool = False
    version: PositiveInt = 2


class TraefikDynamicTcpModel(TraefikDynamicBaseModel):
    hostsni: str | list[GlobalExtract] | None
    proxy_protocol: TraefikDynamicTcpProxyProtocolModel = (
        TraefikDynamicTcpProxyProtocolModel()
    )
    tls: TraefikDynamicTcpTlsModel = TraefikDynamicTcpTlsModel()
