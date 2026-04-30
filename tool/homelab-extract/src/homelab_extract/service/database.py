from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class DatabaseInfoSource(StrEnum):
    USERNAME = auto()
    PASSWORD = auto()
    DATABASE = auto()
    HOST = auto()
    PORT = auto()
    URL = auto()


class ServiceExtractDatabaseSource(HomelabBaseModel):
    type: str
    database: str | None = None
    version: PositiveInt | None = None
    info: DatabaseInfoSource | list[DatabaseInfoSource] | None = None
    scheme: str | None = None
