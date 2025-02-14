from pydantic import BaseModel

from .barman import BarmanConfig
from .restic import ResticConfig


class BackupConfig(BaseModel):
    barman: BarmanConfig
    restic: ResticConfig
