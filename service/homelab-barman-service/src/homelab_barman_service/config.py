from homelab_dagu_service.config.group.docker import DaguDagDockerGroupConfig
from homelab_docker.extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class BarmanConfig(HomelabBaseModel):
    config_dir: GlobalExtract
    staging_dir: GlobalExtract

    minimum_redundancy: PositiveInt
    last_backup_maximum_age: str
    retention_policy: str

    dagu: DaguDagDockerGroupConfig
