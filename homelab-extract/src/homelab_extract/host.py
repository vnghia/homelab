from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class HostInfoSource(StrEnum):
    USER = auto()
    ADDRESS = auto()


class GlobalExtractHostSource(HomelabBaseModel):
    host: HostInfoSource
