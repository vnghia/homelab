from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class KeyInfoSource(StrEnum):
    PRIVATE_PEM = auto()
    PUBLIC_PEM = auto()
    PRIVATE_OPENSSH = auto()
    PUBLIC_OPENSSH = auto()


class ServiceExtractKeySource(HomelabBaseModel):
    key: str
    info: KeyInfoSource | None = None
