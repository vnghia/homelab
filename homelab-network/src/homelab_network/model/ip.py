import dataclasses
from enum import StrEnum, auto
from typing import ClassVar, Self

from homelab_pydantic.model import HomelabRootModel
from pulumi import Output
from pydantic import IPvAnyAddress


class NetworkIpSource(StrEnum):
    TAILSCALE = auto()
    DDNS = auto()


class NetworkIpModel(HomelabRootModel[dict[str, IPvAnyAddress]]):
    V4: ClassVar[str] = "v4"
    V6: ClassVar[str] = "v6"


@dataclasses.dataclass
class NetworkIpOutputModel:
    data: dict[str, Output[IPvAnyAddress]]

    @classmethod
    def from_model(cls, model: NetworkIpModel) -> Self:
        return cls(data={k: Output.from_input(v) for k, v in model.root.items()})
