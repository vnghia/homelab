from homelab_dagu_service.config.group.docker import DaguDagDockerGroupConfig
from homelab_docker.model.service.extract import ServiceExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class BarmanConfig(HomelabBaseModel):
    config_dir: ServiceExtract
    staging_dir: ServiceExtract

    minimum_redundancy: PositiveInt
    last_backup_maximum_age: str
    retention_policy: str

    dagu: DaguDagDockerGroupConfig
