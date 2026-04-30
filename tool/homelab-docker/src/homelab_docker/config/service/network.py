from __future__ import annotations

from typing import Self

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from homelab_vpn.config.service import ServiceVpnConfig

from ...config.docker.network import NetworkEgressType
from ...extract import ExtractorArgs
from ...model.docker.container.host import ContainerHostHostConfig
from ...model.docker.container.network import ContainerBridgeNetworkConfig


class ServiceNetworkEgressHostConfig(HomelabBaseModel):
    host: str
    hostnames: list[GlobalExtract]

    def with_service(self, service: str, force: bool) -> ServiceNetworkEgressHostConfig:
        return self.__replace__(
            hostnames=[
                hostname.with_service(service, force) for hostname in self.hostnames
            ],
        )


class ServiceNetworkEgressFullConfig(HomelabBaseModel):
    addresses: list[GlobalExtract]
    ip: GlobalExtract | None
    proxied: bool

    def with_service(self, service: str, force: bool) -> Self:
        return self.model_construct(
            address=[
                address.with_service(service, force) for address in self.addresses
            ],
            ip=GlobalExtract.with_service_nullable(self.ip, service, force),
        )


class ServiceNetworkEgressDomainConfig(
    HomelabRootModel[
        None
        | GlobalExtract
        | ServiceNetworkEgressHostConfig
        | ServiceNetworkEgressFullConfig
    ]
):
    def to_full(
        self, key: str, extractor_args: ExtractorArgs
    ) -> ServiceNetworkEgressFullConfig:
        root = self.root
        if not root:
            return ServiceNetworkEgressFullConfig(
                addresses=[GlobalExtract.from_simple(key)], ip=None, proxied=True
            )
        if isinstance(root, GlobalExtract):
            return ServiceNetworkEgressFullConfig(
                addresses=[root], ip=None, proxied=True
            )
        if isinstance(root, ServiceNetworkEgressHostConfig):
            ip = ContainerHostHostConfig.get_host_ip(root.host, extractor_args)
            return ServiceNetworkEgressFullConfig(
                addresses=root.hostnames, ip=ip, proxied=False
            )
        return root

    def with_service(self, service: str) -> Self:
        root = self.root
        return self.model_construct(root.with_service(service, False) if root else root)


class ServiceNetworkBridgeConfig(ContainerBridgeNetworkConfig):
    egress: dict[NetworkEgressType, dict[str, ServiceNetworkEgressDomainConfig]] = {}


class ServiceNetworkConfig(HomelabBaseModel):
    vpn: ServiceVpnConfig | None = None
    bridge: ServiceNetworkBridgeConfig | None = ServiceNetworkBridgeConfig()

    @property
    def vpn_(self) -> ServiceVpnConfig:
        if not self.vpn:
            raise ValueError("Service network vpn config is not provided")
        return self.vpn
