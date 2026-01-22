from __future__ import annotations

from enum import StrEnum, auto
from typing import Self

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from homelab_vpn.config.service import ServiceVpnConfig

from ...extract import ExtractorArgs
from ...model.docker.container.host import ContainerHostHostConfig
from ...model.docker.container.network import ContainerBridgeNetworkConfig


class ServiceNetworkProxyEgressType(StrEnum):
    HTTPS = auto()


class ServiceNetworkProxyEgressHostConfig(HomelabBaseModel):
    host: str
    hostnames: list[GlobalExtract]

    def with_service(
        self, service: str, force: bool
    ) -> ServiceNetworkProxyEgressHostConfig:
        return self.__replace__(
            hostnames=[
                hostname.with_service(service, force) for hostname in self.hostnames
            ],
        )


class ServiceNetworkProxyEgressFullConfig(HomelabBaseModel):
    addresses: list[GlobalExtract]
    ip: GlobalExtract | None
    external: bool

    def with_service(self, service: str, force: bool) -> Self:
        return self.model_construct(
            address=[
                address.with_service(service, force) for address in self.addresses
            ],
            ip=GlobalExtract.with_service_nullable(self.ip, service, force),
        )


class ServiceNetworkProxyEgressConfig(
    HomelabRootModel[
        GlobalExtract
        | ServiceNetworkProxyEgressHostConfig
        | ServiceNetworkProxyEgressFullConfig
    ]
):
    def to_full(
        self, extractor_args: ExtractorArgs
    ) -> ServiceNetworkProxyEgressFullConfig:
        root = self.root
        if isinstance(root, GlobalExtract):
            return ServiceNetworkProxyEgressFullConfig(
                addresses=[root], ip=None, external=True
            )
        if isinstance(root, ServiceNetworkProxyEgressHostConfig):
            ip = ContainerHostHostConfig.get_host_ip(root.host, extractor_args)
            return ServiceNetworkProxyEgressFullConfig(
                addresses=root.hostnames, ip=ip, external=False
            )
        return root

    def with_service(self, service: str) -> Self:
        root = self.root
        return self.model_construct(root.with_service(service, False))


class ServiceNetworkProxyConfig(HomelabBaseModel):
    egress: dict[
        ServiceNetworkProxyEgressType, dict[str, ServiceNetworkProxyEgressConfig]
    ] = {}


class ServiceNetworkBridgeConfig(ContainerBridgeNetworkConfig):
    proxy: ServiceNetworkProxyConfig = ServiceNetworkProxyConfig()


class ServiceNetworkConfig(HomelabBaseModel):
    vpn: ServiceVpnConfig | None = None
    bridge: ServiceNetworkBridgeConfig | None = ServiceNetworkBridgeConfig()

    @property
    def vpn_(self) -> ServiceVpnConfig:
        if not self.vpn:
            raise ValueError("Service network vpn config is not provided")
        return self.vpn
