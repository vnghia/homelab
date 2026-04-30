from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class ContainerInfoSource(StrEnum):
    ID = auto()
    NAME = auto()
    DNS = auto()


class ContainerExtractInfoSource(HomelabBaseModel):
    cinfo: ContainerInfoSource
