import dataclasses
from enum import StrEnum, auto
from ipaddress import IPv4Address, IPv6Address
from typing import Self

from homelab_pydantic import HomelabBaseModel
from pulumi import Output
from pydantic import IPvAnyAddress


class NetworkIpSource(StrEnum):
    TAILSCALE = auto()


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

    def to_dict(self) -> dict[str, Output[IPvAnyAddress]]:
        return {"v4": self.v4, "v6": self.v6}
