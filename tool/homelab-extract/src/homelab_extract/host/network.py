from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class HostNetworkInfoSource(StrEnum):
    SUBNET = auto()
    PROXY4 = auto()
    PROXY6 = auto()


class HostExtractNetworkSource(HomelabBaseModel):
    network: str
    info: HostNetworkInfoSource
