from homelab_pydantic import HomelabBaseModel


class GlobalExtractHostnameSource(HomelabBaseModel):
    hostname: str
    public: bool
    scheme: str | None = None
    append_slash: bool = False
