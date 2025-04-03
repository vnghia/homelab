from homelab_pydantic import HomelabBaseModel


class GlobalExtractIdSource(HomelabBaseModel):
    id: str | None
