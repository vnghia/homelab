from pydantic import BaseModel

from .barman import BarmanConfig


class BackupConfig(BaseModel):
    barman: BarmanConfig
