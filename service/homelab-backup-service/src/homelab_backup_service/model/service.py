from homelab_docker.model.database.type import DatabaseType
from homelab_pydantic import HomelabBaseModel


class BackupServiceVolumeModel(HomelabBaseModel):
    pre: bool = False


class BackupServiceModel(HomelabBaseModel):
    volume: BackupServiceVolumeModel | None = None
    databases: dict[DatabaseType, str] = {}
