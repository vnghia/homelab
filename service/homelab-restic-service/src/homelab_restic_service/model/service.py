from homelab_pydantic import HomelabBaseModel


class ResticServiceModel(HomelabBaseModel):
    volume: bool
    postgres: str | None
