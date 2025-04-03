from homelab_pydantic import HomelabBaseModel


class GlobalExtractNameSource(HomelabBaseModel):
    name: str | None
