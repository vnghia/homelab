from homelab_backup.config import BackupHostConfig
from homelab_hatchet_config import HatchetServiceConfigBase
from homelab_restic.model.frequency import BackupFrequency
from pydantic import ConfigDict


class BackupConfig(BackupHostConfig, HatchetServiceConfigBase):
    model_config = ConfigDict(frozen=False)

    schedule: dict[BackupFrequency, str]
