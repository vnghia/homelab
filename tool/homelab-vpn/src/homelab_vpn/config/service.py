from typing import ClassVar

from homelab_pydantic import HomelabRootModel

from ..model import VpnModel


class ServiceVpnConfig(HomelabRootModel[VpnModel]):
    VPN_CONTAINER: ClassVar[str] = "vpn"
