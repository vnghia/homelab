from pydantic import Field

from ...database.type import DatabaseType
from .source.envs import ContainerDatabaseSourceEnvs
from .type import ContainerDatabaseTypeConfig


class ContainerDatabaseRedisConfig(
    ContainerDatabaseTypeConfig[ContainerDatabaseSourceEnvs]
):
    TYPE = DatabaseType.REDIS

    name: str | None = Field(alias="redis")
