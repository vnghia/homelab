from homelab_pydantic import HomelabBaseModel


class Hostname(HomelabBaseModel):
    value: str


class Hostnames(dict[str, dict[str, Hostname]]):
    pass
