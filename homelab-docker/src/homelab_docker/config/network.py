from typing import ClassVar

from pydantic import BaseModel, Field, field_validator

from homelab_docker.model import network


class Network(BaseModel):
    DEFAULT_BRIDGE: ClassVar[str] = "default-bridge"
    INTERNAL_BRIDGE: ClassVar[str] = "internal-bridge"

    default_bridge: network.Bridge = Field(alias="default-bridge")
    internal_bridge: network.Bridge = Field(alias="internal-bridge")

    @field_validator("internal_bridge", mode="after")
    def set_internal_flag(cls, internal_bridge: network.Bridge) -> network.Bridge:
        return internal_bridge.model_copy(update={"internal": True})
