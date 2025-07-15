from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class ServiceDatabasePostgresConfigModel(HomelabBaseModel):
    minimum_redundancy: PositiveInt | None = None
    last_backup_maximum_age: str | None = None
    retention_policy: str | None = None
