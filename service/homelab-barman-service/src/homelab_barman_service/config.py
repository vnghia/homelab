from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract import GlobalExtract
from pydantic import PositiveInt


class BarmanConfig(DaguServiceConfigBase):
    config_dir: GlobalExtract
    staging_dir: GlobalExtract

    minimum_redundancy: PositiveInt
    last_backup_maximum_age: str
    retention_policy: str
