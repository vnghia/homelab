from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, RelativePath

from ..model.sqlite import BackupSqliteModel


class BackupVolumeConfig(HomelabBaseModel):
    repository: str | None = None
    source: GlobalExtract | None = None
    file: bool = False
    excludes: list[RelativePath] = []
    sqlite: BackupSqliteModel | None = None
