from homelab_docker.extract.service import ServiceExtract
from homelab_vpn_config import VpnConfig


class GluetunConfig(VpnConfig):
    opvn: str | None = None
    opvn_path: ServiceExtract
