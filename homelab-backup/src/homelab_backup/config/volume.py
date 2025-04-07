from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class BackupVolumeConfig(HomelabBaseModel):
    enabled: bool = True
    source: GlobalExtract | None = None
    sqlites: list[GlobalExtract] = []

    def __bool__(self) -> bool:
        return self.enabled
