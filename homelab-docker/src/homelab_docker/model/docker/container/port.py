from __future__ import annotations

import typing
from enum import StrEnum, auto
from typing import ClassVar, Literal, Self

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from netaddr_pydantic import IPAddress
from pulumi import Input, Output
from pydantic import PositiveInt

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class ContainerPortProtocol(StrEnum):
    TCP = auto()
    UDP = auto()


class ContainerPortForwardConfig(HomelabBaseModel):
    alias: str | None = None


class ContainerPortConfig(HomelabBaseModel):
    IP_V6: ClassVar[Literal[6]] = 6

    internal: PositiveInt | GlobalExtract
    external: PositiveInt | GlobalExtract
    ip: IPAddress
    protocol: ContainerPortProtocol | None = None
    forward: ContainerPortForwardConfig | None = None

    @classmethod
    def extract_port(
        cls, port: PositiveInt | GlobalExtract, extractor_args: ExtractorArgs
    ) -> Input[PositiveInt]:
        from ....extract.global_ import GlobalExtractor

        if isinstance(port, int):
            return port
        return GlobalExtractor(port).extract_str(extractor_args).apply(int)

    def extract_self(
        self, extractor_args: ExtractorArgs
    ) -> Output[ContainerPortConfig]:
        internal = self.extract_port(self.internal, extractor_args)
        external = self.extract_port(self.external, extractor_args)
        return Output.all(internal=internal, external=external).apply(
            lambda kwargs: self.__replace__(**kwargs)
        )

    def ensure_type(self) -> tuple[PositiveInt, PositiveInt]:
        if not isinstance(self.internal, int) or not isinstance(self.external, int):
            raise TypeError("Ports are not a valid integer")
        return (self.internal, self.external)

    def to_args(self) -> docker.ContainerPortArgs:
        internal, external = self.ensure_type()
        return docker.ContainerPortArgs(
            internal=internal,
            external=external,
            ip=str(self.ip),
            protocol=self.protocol,
        )

    def to_comparable(self) -> tuple[PositiveInt, PositiveInt, int, bool, str]:
        internal, external = self.ensure_type()
        return (
            internal,
            external,
            (2 if self.protocol == ContainerPortProtocol.UDP else 1)
            if self.protocol
            else 0,
            self.ip.version == self.IP_V6,
            str(self.ip),
        )

    def __lt__(self, other: Self) -> bool:
        return self.to_comparable() < other.to_comparable()

    def with_port_service(
        self, port: PositiveInt | GlobalExtract, service: str, force: bool
    ) -> PositiveInt | GlobalExtract:
        if isinstance(port, int):
            return port
        return port.with_service(service, force)

    def with_service(self, service: str, force: bool) -> ContainerPortConfig:
        internal = self.with_port_service(self.internal, service, force)
        external = self.with_port_service(self.external, service, force)
        return self.__replace__(internal=internal, external=external)
