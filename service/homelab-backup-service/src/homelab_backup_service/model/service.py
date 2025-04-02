from homelab_docker.model.database.type import DatabaseType
from homelab_pydantic import HomelabBaseModel


class BackupServiceModel(HomelabBaseModel):
    volume: bool = False
    databases: dict[DatabaseType, str] = {}
