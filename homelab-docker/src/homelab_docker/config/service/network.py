from homelab_pydantic import HomelabBaseModel
from homelab_vpn.config.service import ServiceVpnConfig

from ...model.docker.container.network import ContainerBridgeNetworkConfig


class ServiceNetworkConfig(HomelabBaseModel):
    vpn: ServiceVpnConfig | None = None
    bridge: ContainerBridgeNetworkConfig | None = ContainerBridgeNetworkConfig()

    @property
    def vpn_(self) -> ServiceVpnConfig:
        if not self.vpn:
            raise ValueError("Service network vpn config is not provided")
        return self.vpn
