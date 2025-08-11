from ipaddress import IPv4Address, IPv6Address

from homelab_pydantic import HomelabBaseModel
from pydantic import IPvAnyAddress, PositiveInt

from .port import ContainerPortConfig, ContainerPortForwardConfig, ContainerPortProtocol


class ContainerPortsConfig(HomelabBaseModel):
    internal: PositiveInt | None = None
    external: PositiveInt | None = None
    range: tuple[PositiveInt, PositiveInt] | None = None
    ips: dict[str, IPvAnyAddress] = {
        "v4": IPv4Address("0.0.0.0"),
        "v6": IPv6Address("::"),
    }
    protocol: ContainerPortProtocol | None = None
    forward: ContainerPortForwardConfig | None = None

    def to_ports(self) -> list[ContainerPortConfig]:
        if self.range:
            return [
                ContainerPortConfig(
                    internal=port,
                    external=port,
                    ip=ip,
                    protocol=self.protocol,
                    forward=self.forward,
                )
                for port in range(self.range[0], self.range[1] + 1)
                for ip in self.ips.values()
            ]
        if self.internal:
            external = self.external or self.internal
            return [
                ContainerPortConfig(
                    internal=self.internal,
                    external=external,
                    ip=ip,
                    protocol=self.protocol,
                    forward=self.forward,
                )
                for ip in self.ips.values()
            ]
        raise ValueError(
            "Either internal or range must be specified for container ports config"
        )
