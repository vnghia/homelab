from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class BackupSqliteModel(HomelabBaseModel):
    dbs: list[str | GlobalExtract]
