from ipaddress import IPv4Address

import pulumi_docker as docker
from pydantic import BaseModel, IPvAnyAddress, PositiveInt


class Port(BaseModel):
    internal: PositiveInt
    external: PositiveInt
    ip: IPvAnyAddress

    def to_container_port(self) -> docker.ContainerPortArgs:
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
