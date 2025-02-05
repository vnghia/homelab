from ipaddress import IPv4Address
from typing import Self

import pulumi_docker as docker
from pydantic import BaseModel, IPvAnyAddress, PositiveInt


class Port(BaseModel):
    internal: PositiveInt
    external: PositiveInt
    ip: IPvAnyAddress

    def to_args(self) -> docker.ContainerPortArgs:
        return docker.ContainerPortArgs(
            internal=self.internal,
            external=self.external,
            ip=str(self.ip),
        )

    def to_comparable(self) -> tuple[PositiveInt, PositiveInt, bool, str]:
        return (
            self.internal,
            self.external,
            isinstance(self.ip, IPv4Address),
            str(self.ip),
        )

    def __lt__(self, other: Self) -> bool:
        return self.to_comparable() < other.to_comparable()
