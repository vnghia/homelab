from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class HostInfoSource(StrEnum):
    USER = auto()
    ADDRESS = auto()
    TIMEZONE = auto()


class HostExtractInfoSource(HomelabBaseModel):
    hinfo: HostInfoSource
