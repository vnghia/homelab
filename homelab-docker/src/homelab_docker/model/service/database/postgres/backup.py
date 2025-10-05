from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class ServiceDatabasePostgresBackupConfigModel(HomelabBaseModel):
    minimum_redundancy: PositiveInt | None
    last_backup_maximum_age: str | None
    retention_policy: str | None
