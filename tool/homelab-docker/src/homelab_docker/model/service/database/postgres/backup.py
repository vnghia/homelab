from homelab_pydantic import HomelabBaseModel
from pydantic import NonNegativeInt


class ServiceDatabasePostgresBackupConfigModel(HomelabBaseModel):
    minimum_redundancy: NonNegativeInt | None = None
    last_backup_maximum_age: str | None = None
    retention_policy: str | None = None
    backup_compression: str | None = None
    backup_compression_level: int | None = None
    compression: str | None = None
