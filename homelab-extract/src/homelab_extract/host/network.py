from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class HostNetworkInfoSource(StrEnum):
    SUBNET = auto()


class HostExtractNetworkSource(HomelabBaseModel):
    network: str
    info: HostNetworkInfoSource
