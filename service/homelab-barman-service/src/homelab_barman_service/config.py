from homelab_dagu_config import DaguServiceConfigBase
from homelab_docker.model.service.database.postgres.backup import (
    ServiceDatabasePostgresBackupConfigModel,
)
from homelab_extract import GlobalExtract
from homelab_hatchet_config import HatchetServiceConfigBase


class BarmanConfig(
    ServiceDatabasePostgresBackupConfigModel,
    DaguServiceConfigBase,
    HatchetServiceConfigBase,
):
    config_dir: GlobalExtract
    staging_dir: GlobalExtract
