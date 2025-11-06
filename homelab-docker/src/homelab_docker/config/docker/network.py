from homelab_pydantic import HomelabBaseModel
from homelab_vpn.config.host import HostVpnConfig
from netaddr_pydantic import IPNetwork

from ...model.docker.container.network import ContainerNetworkConfig
from ...model.docker.network import BridgeNetworkModel


class NetworkBridgeConfig(HomelabBaseModel):
    host: dict[str, BridgeNetworkModel]
    service: list[IPNetwork]

    def __getitem__(self, key: str) -> BridgeNetworkModel:
        return self.host[key]


class NetworkConfig(HomelabBaseModel):
    vpn: HostVpnConfig | None = None
    bridge: NetworkBridgeConfig
    default: ContainerNetworkConfig

    @property
    def vpn_(self) -> HostVpnConfig:
        if not self.vpn:
            raise ValueError("Host docker vpn config is not provided")
        return self.vpn
