from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel
from pydantic import NonNegativeInt


class ResticKeepTimeframeType(StrEnum):
    HOURLY = auto()
    DAILY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    YEARLY = auto()


class ResticKeepConfig(HomelabBaseModel):
    last: dict[ResticKeepTimeframeType, NonNegativeInt] = {}
