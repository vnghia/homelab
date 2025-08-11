from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class GluetunOpenVPNConfig(HomelabBaseModel):
    content: GlobalExtract
    path: GlobalExtract


class GluetunConfig(HomelabBaseModel):
    open_vpn: GluetunOpenVPNConfig | None = None
