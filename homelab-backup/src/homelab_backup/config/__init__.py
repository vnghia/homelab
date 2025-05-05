from typing import ClassVar

from homelab_pydantic import HomelabBaseModel


class BackupGlobalConfig(HomelabBaseModel):
    BACKUP_KEY: ClassVar[str] = "BACKUP_KEY"
    BACKUP_KEY_VALUE: ClassVar[str] = "all"

    SNAPSHOT_KEY: ClassVar[str] = "SNAPSHOT_KEY"
    SNAPSHOT_KEY_VALUE: ClassVar[str] = "latest"
