from .base import TraefikDynamicBaseModel


class TraefikDynamicTcpModel(TraefikDynamicBaseModel):
    hostsni: str | None
