from homelab_extract import GlobalExtract

from .base import TraefikDynamicBaseModel


class TraefikDynamicTcpModel(TraefikDynamicBaseModel):
    hostsni: str | list[GlobalExtract] | None
