from pathlib import PosixPath

from homelab_docker.model.container.volume_path import ContainerVolumePath
from pydantic import BaseModel, Field, PositiveInt


class BarmanDaguTaskConfig(BaseModel):
    schedule: str | None = None
    command: list[str]


class BarmanDaguConfig(BaseModel):
    tasks: dict[str, BarmanDaguTaskConfig]
    tags: list[str]


class BarmanConfig(BaseModel):
    config_dir: ContainerVolumePath = Field(alias="config-dir")
    staging_dir: ContainerVolumePath = Field(alias="staging-dir")

    minimum_redundancy: PositiveInt = Field(5, alias="minimum-redundancy")
    last_backup_maximum_age: str = Field("1 WEEKS", alias="last-backup-maximum-age")
    retention_policy: str = Field(
        "RECOVERY WINDOW OF 1 WEEKS", alias="retention-policy"
    )

    dagu: BarmanDaguConfig

    def get_config_container_volume_path(self, file: str) -> ContainerVolumePath:
        return self.config_dir.join(PosixPath(file))
