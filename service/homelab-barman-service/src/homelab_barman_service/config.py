from homelab_dagu_config import DaguServiceConfigBase
from homelab_docker.model.service.database.postgres.backup import (
    ServiceDatabasePostgresBackupConfigModel,
)
from homelab_extract import GlobalExtract


class BarmanConfig(ServiceDatabasePostgresBackupConfigModel, DaguServiceConfigBase):
    config_dir: GlobalExtract
    staging_dir: GlobalExtract
