from homelab_pydantic import HomelabBaseModel
from homelab_vpn.config.host import HostVpnConfig
from pydantic import IPvAnyNetwork

from ...model.docker.container.network import ContainerBridgeNetworkConfig
from ...model.docker.network import BridgeNetworkModel


class NetworkBridgeConfig(HomelabBaseModel):
    host: dict[str, BridgeNetworkModel]
    service: list[IPvAnyNetwork]


class NetworkProxyConfig(HomelabBaseModel):
    service: str
    container: str | None = None
    bridge: ContainerBridgeNetworkConfig = ContainerBridgeNetworkConfig()


class NetworkConfig(HomelabBaseModel):
    vpn: HostVpnConfig | None = None
    bridge: NetworkBridgeConfig
    proxy: NetworkProxyConfig

    @property
    def vpn_(self) -> HostVpnConfig:
        if not self.vpn:
            raise ValueError("Host docker vpn config is not provided")
        return self.vpn
