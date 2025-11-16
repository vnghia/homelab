from homelab_backup.model.frequency import BackupFrequency
from homelab_pydantic import HomelabBaseModel
from pydantic import NonNegativeInt


class ResticKeepConfig(HomelabBaseModel):
    last: dict[BackupFrequency, NonNegativeInt] = {}
    within: dict[BackupFrequency, str] = {}
