from homelab_pydantic import HomelabBaseModel
from pydantic import IPvAnyAddress, PositiveInt

from .port import ContainerPortConfig, ContainerPortForwardConfig, ContainerPortProtocol


class ContainerPortsConfig(HomelabBaseModel):
    start: PositiveInt
    end: PositiveInt
    ip: IPvAnyAddress
    protocol: ContainerPortProtocol | None = None
    forward: ContainerPortForwardConfig | None = None

    def to_ports(self) -> list[ContainerPortConfig]:
        return [
            ContainerPortConfig(
                internal=port,
                external=port,
                ip=self.ip,
                protocol=self.protocol,
                forward=self.forward,
            )
            for port in range(self.start, self.end + 1)
        ]
