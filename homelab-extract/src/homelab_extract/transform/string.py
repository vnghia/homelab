from homelab_pydantic import HomelabBaseModel


class ExtractTransformString(HomelabBaseModel):
    capture: str | None = None
    template: str | None = None
