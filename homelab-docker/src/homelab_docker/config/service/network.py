from homelab_pydantic import HomelabBaseModel
from homelab_vpn.config.service import ServiceVpnConfig


class ServiceNetworkConfig(HomelabBaseModel):
    vpn: ServiceVpnConfig | None = None

    @property
    def vpn_(self) -> ServiceVpnConfig:
        if not self.vpn:
            raise ValueError("Service network vpn config is not provided")
        return self.vpn
