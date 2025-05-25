from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, RelativePath


class BackupVolumeConfig(HomelabBaseModel):
    enabled: bool = True
    source: GlobalExtract | None = None
    file: bool = False
    excludes: list[RelativePath] = []
    sqlites: list[GlobalExtract] = []

    def __bool__(self) -> bool:
        return self.enabled
