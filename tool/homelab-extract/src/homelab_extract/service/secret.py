from homelab_pydantic import HomelabBaseModel


class ServiceExtractSecretSource(HomelabBaseModel):
    secret: str
