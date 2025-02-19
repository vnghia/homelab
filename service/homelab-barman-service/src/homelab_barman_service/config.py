from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class BarmanDaguTaskConfig(HomelabBaseModel):
    schedule: str | None = None
    command: list[str]


class BarmanDaguConfig(HomelabBaseModel):
    tasks: dict[str, BarmanDaguTaskConfig]
    tags: list[str]


class BarmanConfig(HomelabBaseModel):
    config_dir: ContainerVolumePath
    staging_dir: ContainerVolumePath

    minimum_redundancy: PositiveInt = 5
    last_backup_maximum_age: str = "1 WEEKS"
    retention_policy: str = "RECOVERY WINDOW OF 1 WEEKS"

    dagu: BarmanDaguConfig

    def get_config_container_volume_path(self, file: str) -> ContainerVolumePath:
        return self.config_dir / file
