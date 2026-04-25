from .model import HomelabBaseModel


class Hostname(HomelabBaseModel):
    zone: str
    name: str
    value: str


class Hostnames(dict[str, dict[str, Hostname]]):
    pass
