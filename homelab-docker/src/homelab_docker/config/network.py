from typing import ClassVar

from pydantic import BaseModel, field_validator

from homelab_docker import model


class Network(BaseModel):
    DEFAULT_BRIDGE: ClassVar[str] = "default-bridge"
    INTERNAL_BRIDGE: ClassVar[str] = "internal-bridge"

    default_bridge: model.BridgeNetwork
    internal_bridge: model.BridgeNetwork

    @field_validator("internal_bridge", mode="after")
    def set_internal_flag(
        cls, internal_bridge: model.BridgeNetwork
    ) -> model.BridgeNetwork:
        return internal_bridge.model_copy(update={"internal": True})
