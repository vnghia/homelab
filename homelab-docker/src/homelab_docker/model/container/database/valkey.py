from pydantic import Field

from ...database.type import DatabaseType
from .source.envs import ContainerDatabaseSourceEnvs
from .source.redis.url import ContainerDatabaseRedisSourceUrlEnvs
from .type import ContainerDatabaseTypeConfig


class ContainerDatabaseValkeyConfig(
    ContainerDatabaseTypeConfig[
        ContainerDatabaseRedisSourceUrlEnvs | ContainerDatabaseSourceEnvs
    ]
):
    TYPE = DatabaseType.VALKEY

    name: str | None = Field(alias="valkey")
