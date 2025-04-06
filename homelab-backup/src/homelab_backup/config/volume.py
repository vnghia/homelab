from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class BackupVolumeConfig(HomelabBaseModel):
    source: GlobalExtract | None = None
    sqlites: list[GlobalExtract] = []
