from homelab_backup.config import BackupGlobalConfig
from pydantic import PositiveInt


class BackupConfig(BackupGlobalConfig):
    schedule: str
    max_concurent: PositiveInt | None = None
