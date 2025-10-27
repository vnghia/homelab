from homelab_pydantic import HomelabBaseModel


class ServiceExtractVpnSource(HomelabBaseModel):
    port: str | None
