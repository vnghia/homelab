from homelab_pydantic import HomelabBaseModel


class ServiceMoveConfig(HomelabBaseModel):
    host: str
