from homelab_extract import GlobalExtract

from .base import VpnBaseModel


class VpnWireguardModel(VpnBaseModel):
    addresses: list[GlobalExtract]
    private_key: GlobalExtract
    preshared_key: GlobalExtract
