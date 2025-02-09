from homelab_docker.model.container.volume_path import ContainerVolumePath
from pydantic import BaseModel, Field, PositiveInt


class BarmanConfig(BaseModel):
    config_dir: ContainerVolumePath = Field(alias="config-dir")
    staging_dir: ContainerVolumePath = Field(alias="staging-dir")
    minimum_redundancy: PositiveInt = Field(5, alias="minimum-redundancy")
    retention_policy: str = Field(
        "RECOVERY WINDOW OF 1 WEEKS", alias="retention-policy"
    )

    def get_config_container_volume_path(self, file: str) -> ContainerVolumePath:
        return self.config_dir.model_copy(
            update={"path": (self.config_dir.path / file).with_suffix(".conf")}
        )
