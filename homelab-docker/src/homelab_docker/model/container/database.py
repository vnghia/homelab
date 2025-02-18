from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output
from pydantic import Field, PositiveInt

from ..database.source import DatabaseSourceModel
from ..database.source.postgres.url import PostgresDatabaseSourceUrlEnvs

if typing.TYPE_CHECKING:
    from ...config.database import DatabaseConfig
    from ...config.database.source import DatabaseSourceConfig


class ContainerPostgresDatabaseConfig(HomelabBaseModel):
    name: str | None = Field(alias="postgres")
    version: PositiveInt | None = None
    envs: PostgresDatabaseSourceUrlEnvs | None = None

    def to_database_version(self, database_config: DatabaseConfig) -> PositiveInt:
        model = database_config.postgres[self.name]
        return self.version or model.versions[0]

    def to_container_name(
        self, service_name: str, database_config: DatabaseConfig
    ) -> str:
        from ..database.postgres import PostgresDatabaseModel

        return PostgresDatabaseModel.get_full_name_version(
            service_name, self.name, self.to_database_version(database_config)
        )

    def to_database_source_model(
        self,
        database_config: DatabaseConfig,
        database_source_config: DatabaseSourceConfig,
    ) -> DatabaseSourceModel:
        return database_source_config.postgres[self.name][
            self.to_database_version(database_config)
        ]

    def build_envs(
        self,
        database_config: DatabaseConfig,
        database_source_config: DatabaseSourceConfig,
    ) -> dict[str, Output[str]]:
        if self.envs:
            source_model = self.to_database_source_model(
                database_config, database_source_config
            )
            return self.envs.to_envs(source_model)
        else:
            return {}


class ContainerDatabaseConfig(HomelabRootModel[ContainerPostgresDatabaseConfig]):
    def to_database_version(self, database_config: DatabaseConfig) -> PositiveInt:
        return self.root.to_database_version(database_config)

    def to_container_name(
        self, service_name: str, database_config: DatabaseConfig
    ) -> str:
        return self.root.to_container_name(service_name, database_config)

    def build_envs(
        self,
        database_config: DatabaseConfig,
        database_source_config: DatabaseSourceConfig,
    ) -> dict[str, Output[str]]:
        return self.root.build_envs(database_config, database_source_config)
