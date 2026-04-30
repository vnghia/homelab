from homelab_pydantic import HomelabBaseModel
from pydantic import NonNegativeInt

from .frequency import BackupFrequency


class ResticKeepConfig(HomelabBaseModel):
    last: dict[BackupFrequency, NonNegativeInt] = {}
    within: dict[BackupFrequency, str] = {}

    def to_forget_options(self) -> dict[str, NonNegativeInt | str]:
        return {
            "keep-{}".format(timeframe): number
            for timeframe, number in self.last.items()
        } | {
            "keep-within-{}".format(timeframe): duration
            for timeframe, duration in self.within.items()
        }
