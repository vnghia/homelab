from homelab_pydantic import HomelabBaseModel

from .backup import ServiceDatabasePostgresBackupConfigModel


class ServiceDatabasePostgresConfigModel(HomelabBaseModel):
    backup: ServiceDatabasePostgresBackupConfigModel | None = None
