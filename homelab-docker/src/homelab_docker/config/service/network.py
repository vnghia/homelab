from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_vpn.config.service import ServiceVpnConfig

from ...model.docker.container.network import ContainerBridgeNetworkConfig


class ServiceNetworkProxyConfig(HomelabBaseModel):
    aliases: list[GlobalExtract] = []


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
