from enum import StrEnum, auto
from ipaddress import IPv6Address
from typing import Self

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pydantic import IPvAnyAddress, PositiveInt


class ContainerPortProtocol(StrEnum):
    TCP = auto()
    UDP = auto()


class ContainerPortForwardConfig(HomelabBaseModel):
    alias: str | None = None


class ContainerPortConfig(HomelabBaseModel):
    internal: PositiveInt
    external: PositiveInt
    ip: IPvAnyAddress
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
            isinstance(self.ip, IPv6Address),
            str(self.ip),
        )

    def __lt__(self, other: Self) -> bool:
        return self.to_comparable() < other.to_comparable()
