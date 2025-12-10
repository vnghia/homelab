from homelab_backup.config import BackupHostConfig
from homelab_dagu_config import DaguServiceConfigBase
from homelab_restic.model.frequency import BackupFrequency
from pydantic import ConfigDict, PositiveInt


class BackupConfig(BackupHostConfig, DaguServiceConfigBase):
    model_config = ConfigDict(frozen=False)

    schedule: dict[BackupFrequency, str]
    max_concurent: PositiveInt | None = None
