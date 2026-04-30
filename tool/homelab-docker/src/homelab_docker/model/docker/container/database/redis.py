from pydantic import Field

from ....database.type import DatabaseType
from .source.envs import ContainerDatabaseSourceEnvs
from .source.redis.url import ContainerDatabaseRedisSourceUrlEnvs
from .type import ContainerDatabaseTypeConfig


class ContainerDatabaseRedisConfig(
    ContainerDatabaseTypeConfig[
        ContainerDatabaseRedisSourceUrlEnvs | ContainerDatabaseSourceEnvs
    ]
):
    TYPE = DatabaseType.REDIS

    name: str | None = Field(alias="redis")
