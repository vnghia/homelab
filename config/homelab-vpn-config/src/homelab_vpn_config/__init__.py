from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabServiceConfigDict
from pydantic import PositiveInt


class VpnConfig(HomelabBaseModel):
    forwarding_ports: list[PositiveInt] = []


class VpnServiceConfig(HomelabServiceConfigDict[VpnConfig]):
    NONE_KEY = "vpn"


class VpnServiceConfigBase(HomelabBaseModel):
    vpn: VpnServiceConfig = VpnServiceConfig({})
