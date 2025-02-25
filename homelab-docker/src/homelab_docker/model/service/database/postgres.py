from pathlib import PosixPath
from typing import ClassVar

from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pydantic import PositiveInt

from ...container.network import ContainerNetworkConfig
from ...database.type import DatabaseType


class ServicePostgresDatabaseModel(HomelabBaseModel):
    DATABASE_TYPE: ClassVar[DatabaseType] = DatabaseType.POSTGRES
    DATABASE_VERSION: ClassVar[PositiveInt] = 16

    DATABASE_ENTRYPOINT_INITDB_VOLUME: ClassVar[str] = (
        "postgres-docker-entrypoint-initdb"
    )
    DATABASE_ENTRYPOINT_INITDB_PATH: ClassVar[AbsolutePath] = AbsolutePath(
        PosixPath("/docker-entrypoint-initdb.d")
    )

    PGRUN_PATH: ClassVar[AbsolutePath] = AbsolutePath(PosixPath("/var/run/postgresql"))
    PGDATA_PATH: ClassVar[AbsolutePath] = AbsolutePath(
        PosixPath("/var/lib/postgresql/data")
    )
    PORT: ClassVar[PositiveInt] = 5432

    PASSWORD_LENGTH: ClassVar[PositiveInt] = 64

    image: str = DatabaseType.POSTGRES
    versions: list[PositiveInt] = [DATABASE_VERSION]

    username: str | None = None
    database: str | None = None

    network: ContainerNetworkConfig = ContainerNetworkConfig()
