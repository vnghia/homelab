from pydantic import Field

from ...database.type import DatabaseType
from .source.envs import ContainerDatabaseSourceEnvs
from .source.mysql.url import ContainerDatabaseMysqlSourceUrlEnvs
from .type import ContainerDatabaseTypeConfig


class ContainerDatabaseMysqlConfig(
    ContainerDatabaseTypeConfig[
        ContainerDatabaseMysqlSourceUrlEnvs | ContainerDatabaseSourceEnvs
    ]
):
    TYPE = DatabaseType.MYSQL

    name: str | None = Field(alias="mysql")
