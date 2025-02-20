from typing import ClassVar

from homelab_pydantic import HomelabBaseModel


class BackupConfig(HomelabBaseModel):
    BACKUP_PROFILE_KEY: ClassVar[str] = "BACKUP_PROFILE"
    BACKUP_PROFILE_VALUE: ClassVar[str] = "all"
