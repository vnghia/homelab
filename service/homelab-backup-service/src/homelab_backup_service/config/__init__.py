from homelab_backup.config import BackupGlobalConfig
from homelab_backup.model.frequency import BackupFrequency
from homelab_dagu_config import DaguServiceConfigBase
from pydantic import ConfigDict, PositiveInt


class BackupConfig(BackupGlobalConfig, DaguServiceConfigBase):
    model_config = ConfigDict(frozen=False)

    schedule: dict[BackupFrequency, str]
    max_concurent: PositiveInt | None = None
