from pydantic import BaseModel

from homelab_backup_service.config.restic import ResticConfig

from .barman import BarmanConfig


class BackupConfig(BaseModel):
    barman: BarmanConfig
    restic: ResticConfig
