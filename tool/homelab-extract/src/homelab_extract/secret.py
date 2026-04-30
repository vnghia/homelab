from homelab_pydantic import HomelabBaseModel


class GlobalExtractSecretSource(HomelabBaseModel):
    gsecret: str
