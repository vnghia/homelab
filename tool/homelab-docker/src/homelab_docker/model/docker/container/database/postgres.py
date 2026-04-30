from pydantic import Field

from ....database.type import DatabaseType
from .source.envs import ContainerDatabaseSourceEnvs
from .source.postgres.url import ContainerDatabasePostgresSourceUrlEnvs
from .type import ContainerDatabaseTypeConfig


class ContainerDatabasePostgresConfig(
    ContainerDatabaseTypeConfig[
        ContainerDatabasePostgresSourceUrlEnvs | ContainerDatabaseSourceEnvs
    ]
):
    TYPE = DatabaseType.POSTGRES

    name: str | None = Field(alias="postgres")
