from typing import ClassVar

from homelab_pydantic import HomelabBaseModel


class BackupConfig(HomelabBaseModel):
    BACKUP_KEY: ClassVar[str] = "BACKUP_KEY"
    BACKUP_KEY_VALUE: ClassVar[str] = "all"
