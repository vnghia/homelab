from homelab_pydantic import HomelabBaseModel


class Hostname(HomelabBaseModel):
    value: str
    public: bool


class Hostnames(dict[str, dict[str, Hostname]]):
    pass
