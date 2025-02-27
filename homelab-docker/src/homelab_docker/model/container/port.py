from ipaddress import IPv4Address
from typing import Self

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pydantic import IPvAnyAddress, PositiveInt


class ContainerPortConfig(HomelabBaseModel):
    internal: PositiveInt
    external: PositiveInt
    ip: IPvAnyAddress
    protocol: str | None = None

    def to_args(self) -> docker.ContainerPortArgs:
        return docker.ContainerPortArgs(
            internal=self.internal,
            external=self.external,
            ip=str(self.ip),
            protocol=self.protocol,
        )

    def to_comparable(self) -> tuple[PositiveInt, PositiveInt, bool, str, str | None]:
        return (
            self.internal,
            self.external,
            isinstance(self.ip, IPv4Address),
            str(self.ip),
            self.protocol,
        )

    def __lt__(self, other: Self) -> bool:
        return self.to_comparable() < other.to_comparable()
