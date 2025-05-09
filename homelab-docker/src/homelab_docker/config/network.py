from typing import ClassVar

from homelab_pydantic import HomelabBaseModel
from pydantic import field_validator

from ..model.network import BridgeNetworkModel


class NetworkConfig(HomelabBaseModel):
    DEFAULT_BRIDGE: ClassVar[str] = "default-bridge"
    INTERNAL_BRIDGE: ClassVar[str] = "internal-bridge"
    PROXY_BRIDGE: ClassVar[str] = "proxy-bridge"

    default_bridge: BridgeNetworkModel
    internal_bridge: BridgeNetworkModel
    proxy_bridge: BridgeNetworkModel

    @field_validator("internal_bridge", "proxy_bridge", mode="after")
    def set_internal_flag(
        cls, internal_bridge: BridgeNetworkModel
    ) -> BridgeNetworkModel:
        return internal_bridge.__replace__(internal=True)
