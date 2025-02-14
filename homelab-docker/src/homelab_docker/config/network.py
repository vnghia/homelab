from typing import ClassVar

from pydantic import BaseModel, Field, field_validator

from ..model.network import BridgeNetworkModel


class NetworkConfig(BaseModel):
    DEFAULT_BRIDGE: ClassVar[str] = "default-bridge"
    INTERNAL_BRIDGE: ClassVar[str] = "internal-bridge"

    default_bridge: BridgeNetworkModel = Field(alias="default-bridge")
    internal_bridge: BridgeNetworkModel = Field(alias="internal-bridge")

    @field_validator("internal_bridge", mode="after")
    def set_internal_flag(
        cls, internal_bridge: BridgeNetworkModel
    ) -> BridgeNetworkModel:
        return internal_bridge.model_copy(update={"internal": True})
