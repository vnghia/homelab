from typing import ClassVar

from homelab_pydantic import HomelabBaseModel
from pydantic import field_validator

from ...model.docker.network import BridgeNetworkModel


class NetworkConfig(HomelabBaseModel):
    DEFAULT_BRIDGE: ClassVar[str] = "default-bridge"
    INTERNAL_BRIDGE: ClassVar[str] = "internal-bridge"
    PROXY_BRIDGE: ClassVar[str] = "proxy-bridge"

    PROXY_ALIAS: ClassVar[str] = "reverse-proxy"

    default_bridge: BridgeNetworkModel
    internal_bridge: BridgeNetworkModel
    proxy_bridge: BridgeNetworkModel | None = None

    @field_validator("internal_bridge", mode="after")
    def set_internal_flag(
        cls, internal_bridge: BridgeNetworkModel
    ) -> BridgeNetworkModel:
        return internal_bridge.__replace__(internal=True)

    @field_validator("proxy_bridge", mode="after")
    def set_proxy_flag(
        cls, proxy_bridge: BridgeNetworkModel | None
    ) -> BridgeNetworkModel | None:
        return proxy_bridge.__replace__(internal=True) if proxy_bridge else None
