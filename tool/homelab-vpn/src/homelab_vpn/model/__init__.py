from homelab_pydantic import HomelabRootModel

from .wireguard import VpnWireguardModel


class VpnModel(HomelabRootModel[VpnWireguardModel]):
    pass
