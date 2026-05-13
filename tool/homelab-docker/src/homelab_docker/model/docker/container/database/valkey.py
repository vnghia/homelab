from homelab_pydantic import DatabaseType
from pydantic import Field

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
