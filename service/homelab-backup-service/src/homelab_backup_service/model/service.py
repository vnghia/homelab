from homelab_pydantic import DatabaseType, HomelabBaseModel


class BackupServiceVolumeModel(HomelabBaseModel):
    pre: bool = False


class BackupServiceModel(HomelabBaseModel):
    volume: BackupServiceVolumeModel | None = None
    databases: dict[DatabaseType, str] = {}
