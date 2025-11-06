from homelab_pydantic import HomelabBaseModel
from homelab_vpn.config.host import HostVpnConfig

from ...model.docker.container.network import ContainerNetworkConfig
from ...model.docker.network import BridgeNetworkModel


class NetworkConfig(HomelabBaseModel):
    vpn: HostVpnConfig | None = None
    bridge: dict[str, BridgeNetworkModel]
    default: ContainerNetworkConfig

    @property
    def vpn_(self) -> HostVpnConfig:
        if not self.vpn:
            raise ValueError("Host docker vpn config is not provided")
        return self.vpn
