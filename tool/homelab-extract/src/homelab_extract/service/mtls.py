from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class MTlsInfoSourceModel(StrEnum):
    CA_CERT = auto()
    SERVER_KEY = auto()
    SERVER_CERT = auto()
    CLIENT_KEY = auto()
    CLIENT_CERT = auto()


class ServiceExtractMTlsSource(HomelabBaseModel):
    mtls: str
    info: MTlsInfoSourceModel | None
