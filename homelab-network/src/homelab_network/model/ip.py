import dataclasses
from enum import StrEnum, auto
from typing import Self

from homelab_pydantic import HomelabBaseModel
from netaddr_pydantic import IPAddress, IPv4Address, IPv6Address
from pulumi import Output


class NetworkIpSource(StrEnum):
    TAILSCALE = auto()
    DDNS = auto()


class NetworkIpModel(HomelabBaseModel):
    v4: IPv4Address
    v6: IPv6Address


@dataclasses.dataclass
class NetworkIpOutputModel:
    v4: Output[IPv4Address]
    v6: Output[IPv6Address]

    @classmethod
    def from_model(cls, model: NetworkIpModel) -> Self:
        return cls(v4=Output.from_input(model.v4), v6=Output.from_input(model.v6))

    def to_dict(self) -> dict[str, Output[IPAddress]]:
        return {"v4": self.v4, "v6": self.v6}
