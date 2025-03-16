from homelab_pydantic import HomelabBaseModel


class ContainerVpnConfig(HomelabBaseModel):
    port: str
