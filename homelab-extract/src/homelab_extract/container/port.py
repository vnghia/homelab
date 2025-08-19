from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class ContainerPortSource(StrEnum):
    INTERNAL = auto()
    EXTERNAL = auto()


class ContainerExtractPortSource(HomelabBaseModel):
    port: str
    info: ContainerPortSource
