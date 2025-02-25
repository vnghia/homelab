from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output
from pydantic import Field, PositiveInt

from ...database.type import DatabaseType
from .source import ContainerDatabaseSourceModel
from .source.postgres.url import ContainerPostgresDatabaseSourceUrlEnvs

if typing.TYPE_CHECKING:
    from ....config.service.database import ServiceDatabaseConfig
    from ....config.service.database.source import ServiceDatabaseSourceConfig


class ContainerPostgresDatabaseConfig(HomelabBaseModel):
    name: str | None = Field(alias="postgres")
    version: PositiveInt | None = None
    envs: ContainerPostgresDatabaseSourceUrlEnvs | None = None

    def to_database_version(
        self, database_config: ServiceDatabaseConfig
    ) -> PositiveInt:
        model = database_config.root[DatabaseType.POSTGRES][self.name]
        return self.version or model.versions[0]

    def to_container_name(
        self, service_name: str, database_config: ServiceDatabaseConfig
    ) -> str:
        from ...database.type import DatabaseType

        return DatabaseType.POSTGRES.get_full_name_version(
            service_name, self.name, self.to_database_version(database_config)
        )

    def to_database_source_model(
        self,
        database_config: ServiceDatabaseConfig,
        database_source_config: ServiceDatabaseSourceConfig,
    ) -> ContainerDatabaseSourceModel:
        return database_source_config.postgres[self.name][
            self.to_database_version(database_config)
        ]

    def build_envs(
        self,
        database_config: ServiceDatabaseConfig,
        database_source_config: ServiceDatabaseSourceConfig,
    ) -> dict[str, Output[str]]:
        if self.envs:
            source_model = self.to_database_source_model(
                database_config, database_source_config
            )
            return self.envs.to_envs(source_model)
        else:
            return {}


class ContainerDatabaseConfig(HomelabRootModel[ContainerPostgresDatabaseConfig]):
    def to_database_version(
        self, database_config: ServiceDatabaseConfig
    ) -> PositiveInt:
        return self.root.to_database_version(database_config)

    def to_container_name(
        self, service_name: str, database_config: ServiceDatabaseConfig
    ) -> str:
        return self.root.to_container_name(service_name, database_config)

    def build_envs(
        self,
        database_config: ServiceDatabaseConfig,
        database_source_config: ServiceDatabaseSourceConfig,
    ) -> dict[str, Output[str]]:
        return self.root.build_envs(database_config, database_source_config)
