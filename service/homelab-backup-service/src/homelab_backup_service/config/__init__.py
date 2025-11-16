from homelab_backup.config import BackupGlobalConfig
from homelab_dagu_config import DaguServiceConfigBase
from pydantic import ConfigDict, PositiveInt


class BackupConfig(BackupGlobalConfig, DaguServiceConfigBase):
    model_config = ConfigDict(frozen=False)

    schedule: str
    max_concurent: PositiveInt | None = None
