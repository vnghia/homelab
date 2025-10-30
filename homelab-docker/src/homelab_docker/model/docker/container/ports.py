from __future__ import annotations

import typing

import netaddr
import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabRootModel
from netaddr_pydantic import IPAddress
from pulumi import Output
from pydantic import PositiveInt

from .port import ContainerPortConfig, ContainerPortForwardConfig, ContainerPortProtocol

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class ContainerPortRangeConfig(HomelabBaseModel):
    internal: PositiveInt | GlobalExtract | None = None
    external: PositiveInt | GlobalExtract | None = None
    range: tuple[PositiveInt, PositiveInt] | None = None
    ips: dict[str, IPAddress] = {
        "v4": netaddr.IPAddress("0.0.0.0"),
        "v6": netaddr.IPAddress("::"),
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


class ContainerPortsConfig(
    HomelabRootModel[dict[str, ContainerPortRangeConfig | ContainerPortConfig]]
):
    root: dict[str, ContainerPortRangeConfig | ContainerPortConfig] = {}

    def to_args(
        self, extractor_args: ExtractorArgs
    ) -> Output[list[docker.ContainerPortArgs]]:
        ports: list[Output[ContainerPortConfig]] = []
        for config in self.root.values():
            if isinstance(config, ContainerPortConfig):
                ports.append(config.extract_self(extractor_args))
            else:
                ports += [
                    port.extract_self(extractor_args) for port in config.to_ports()
                ]
        return Output.all(*ports).apply(
            lambda ports: ([port.to_args() for port in sorted(ports)])
        )
