from enum import StrEnum, auto
from typing import ClassVar, Literal, Self

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from netaddr_pydantic import IPAddress
from pydantic import PositiveInt


class ContainerPortProtocol(StrEnum):
    TCP = auto()
    UDP = auto()


class ContainerPortForwardConfig(HomelabBaseModel):
    alias: str | None = None


class ContainerPortConfig(HomelabBaseModel):
    IP_V6: ClassVar[Literal[6]] = 6

    internal: PositiveInt
    external: PositiveInt
    ip: IPAddress
    protocol: ContainerPortProtocol | None = None
    forward: ContainerPortForwardConfig | None = None

    def to_args(self) -> docker.ContainerPortArgs:
        return docker.ContainerPortArgs(
            internal=self.internal,
            external=self.external,
            ip=str(self.ip),
            protocol=self.protocol,
        )

    def to_comparable(self) -> tuple[PositiveInt, PositiveInt, int, bool, str]:
        return (
            self.internal,
            self.external,
            (2 if self.protocol == ContainerPortProtocol.UDP else 1)
            if self.protocol
            else 0,
            self.ip.version == self.IP_V6,
            str(self.ip),
        )

    def __lt__(self, other: Self) -> bool:
        return self.to_comparable() < other.to_comparable()
