from pydantic import BaseModel

from .restic import ResticConfig


class BackupConfig(BaseModel):
    restic: ResticConfig
