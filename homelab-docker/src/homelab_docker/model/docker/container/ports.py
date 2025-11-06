from __future__ import annotations

import typing
from typing import Self

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel, IPvAnyAddressAdapter
from pulumi import Output
from pydantic import ConfigDict, IPvAnyAddress, PositiveInt

from .port import ContainerPortConfig, ContainerPortForwardConfig, ContainerPortProtocol

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs
    from . import ContainerModelBuildArgs


class ContainerPortRangeConfig(HomelabBaseModel):
    internal: PositiveInt | GlobalExtract | None = None
    external: PositiveInt | GlobalExtract | None = None
    range: tuple[PositiveInt, PositiveInt] | None = None
    ips: dict[str, IPvAnyAddress] = {
        "v4": IPvAnyAddressAdapter.validate_python("0.0.0.0"),
        "v6": IPvAnyAddressAdapter.validate_python("::"),
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

    def with_port_service(
        self, port: PositiveInt | GlobalExtract | None, service: str, force: bool
    ) -> PositiveInt | GlobalExtract | None:
        if isinstance(port, int):
            return port
        return GlobalExtract.with_service_nullable(port, service, force)

    def with_service(self, service: str, force: bool) -> ContainerPortRangeConfig:
        internal = self.with_port_service(self.internal, service, force)
        external = self.with_port_service(self.external, service, force)
        return self.__replace__(internal=internal, external=external)


class ContainerPortsConfig(
    HomelabRootModel[dict[str, ContainerPortRangeConfig | ContainerPortConfig]]
):
    model_config = ConfigDict(frozen=False)

    root: dict[str, ContainerPortRangeConfig | ContainerPortConfig] = {}

    def to_args(
        self, extractor_args: ExtractorArgs, build_args: ContainerModelBuildArgs
    ) -> Output[list[docker.ContainerPortArgs]]:
        ports: list[Output[ContainerPortConfig]] = []
        for config in (self | build_args.network.ports).root.values():
            if isinstance(config, ContainerPortConfig):
                ports.append(config.extract_self(extractor_args))
            else:
                ports += [
                    port.extract_self(extractor_args) for port in config.to_ports()
                ]
        return Output.all(*ports).apply(
            lambda ports: ([port.to_args() for port in sorted(ports)])
        )

    def __bool__(self) -> bool:
        return bool(self.root)

    def __or__(self, rhs: ContainerPortsConfig) -> ContainerPortsConfig:
        return ContainerPortsConfig(self.root | rhs.root)

    def __ior__(self, rhs: ContainerPortsConfig) -> ContainerPortsConfig:
        self.root |= rhs.root
        return self

    def with_service(self, service: str, force: bool) -> Self:
        return self.model_construct(
            {k: v.with_service(service, force) for k, v in self.root.items()}
        )
