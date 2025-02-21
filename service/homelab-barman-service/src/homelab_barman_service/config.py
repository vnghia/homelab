from homelab_dagu_service.config.group.docker import DaguDagDockerGroupConfig
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class BarmanConfig(HomelabBaseModel):
    config_dir: ContainerVolumePath
    staging_dir: ContainerVolumePath

    minimum_redundancy: PositiveInt
    last_backup_maximum_age: str
    retention_policy: str

    dagu: DaguDagDockerGroupConfig

    def get_config_container_volume_path(self, file: str) -> ContainerVolumePath:
        return self.config_dir / file
