from enum import StrEnum, auto
from typing import Self

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from homelab_vpn.config.service import ServiceVpnConfig

from ...extract import ExtractorArgs
from ...model.docker.container.host import ContainerHostConfig
from ...model.docker.container.network import ContainerBridgeNetworkConfig


class ServiceNetworkProxyEgressType(StrEnum):
    HTTPS = auto()


class ServiceNetworkProxyEgressFullConfig(HomelabBaseModel):
    address: GlobalExtract
    ip: GlobalExtract | None

    def with_service(self, service: str, force: bool) -> Self:
        return self.model_construct(
            address=self.address.with_service(service, force),
            ip=GlobalExtract.with_service_nullable(self.ip, service, force),
        )


class ServiceNetworkProxyEgressConfig(
    HomelabRootModel[
        GlobalExtract | ContainerHostConfig | ServiceNetworkProxyEgressFullConfig
    ]
):
    def to_full(
        self, extractor_args: ExtractorArgs
    ) -> ServiceNetworkProxyEgressFullConfig:
        root = self.root
        if isinstance(root, GlobalExtract):
            return ServiceNetworkProxyEgressFullConfig(address=root, ip=None)
        if isinstance(root, ContainerHostConfig):
            full = root.to_full(extractor_args)
            return ServiceNetworkProxyEgressFullConfig(address=full.host, ip=full.ip)
        return root

    def with_service(self, service: str) -> Self:
        root = self.root
        return self.model_construct(root.with_service(service, False))


class ServiceNetworkProxyConfig(HomelabBaseModel):
    aliases: list[GlobalExtract] = []
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
