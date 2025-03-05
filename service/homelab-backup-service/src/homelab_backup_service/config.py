from homelab_backup.config import BackupGlobalConfig
from homelab_dagu_config import DaguServiceConfigBase


class BackupConfig(BackupGlobalConfig, DaguServiceConfigBase):
    pass
