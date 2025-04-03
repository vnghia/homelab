from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class KeepassInfoSource(StrEnum):
    USERNAME = auto()
    PASSWORD = auto()


class ServiceExtractKeepassSource(HomelabBaseModel):
    keepass: str | None
    info: KeepassInfoSource
