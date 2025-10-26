from homelab_pydantic import HomelabBaseModel


class HostVpnConfig(HomelabBaseModel):
    service: str
    container: str | None = None
