from typing import ClassVar

from homelab_pydantic import HomelabBaseModel


class BackupGlobalConfig(HomelabBaseModel):
    BACKUP_KEY: ClassVar[str] = "BACKUP_KEY"
    BACKUP_KEY_VALUE: ClassVar[str] = "all"
