from __future__ import annotations

import typing

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output
from pydantic import Field, PositiveInt

from ...database.type import DatabaseType
from .source import ContainerDatabaseSourceModel
from .source.postgres.url import ContainerPostgresDatabaseSourceUrlEnvs

if typing.TYPE_CHECKING:
    from ....resource.service.database import ServiceDatabaseResource


class ContainerPostgresDatabaseConfig(HomelabBaseModel):
    name: str | None = Field(alias="postgres")
    version: PositiveInt | None = None
    envs: ContainerPostgresDatabaseSourceUrlEnvs | None = None

    def to_database_version(
        self, database_resource: ServiceDatabaseResource
    ) -> PositiveInt:
        return (
            self.version
            or database_resource.resources[DatabaseType.POSTGRES][self.name].versions[0]
        )

    def to_container(
        self, database_resource: ServiceDatabaseResource
    ) -> docker.Container:
        return database_resource.resources[DatabaseType.POSTGRES][self.name].containers[
            self.to_database_version(database_resource)
        ]

    def to_container_name(self, database_resource: ServiceDatabaseResource) -> str:
        return database_resource.resources[DatabaseType.POSTGRES][
            self.name
        ].get_full_name_version(self.to_database_version(database_resource))

    def to_database_source_model(
        self, database_resource: ServiceDatabaseResource
    ) -> ContainerDatabaseSourceModel:
        return database_resource.source_config[DatabaseType.POSTGRES][self.name][
            self.to_database_version(database_resource)
        ]

    def build_envs(
        self, database_resource: ServiceDatabaseResource
    ) -> dict[str, Output[str]]:
        if self.envs:
            source_model = self.to_database_source_model(database_resource)
            return self.envs.to_envs(source_model)
        else:
            return {}


class ContainerDatabaseConfig(HomelabRootModel[ContainerPostgresDatabaseConfig]):
    def to_database_version(
        self, database_resource: ServiceDatabaseResource
    ) -> PositiveInt:
        return self.root.to_database_version(database_resource)

    def to_container(
        self, database_resource: ServiceDatabaseResource
    ) -> docker.Container:
        return self.root.to_container(database_resource)

    def to_container_name(self, database_resource: ServiceDatabaseResource) -> str:
        return self.root.to_container_name(database_resource)

    def build_envs(
        self, database_resource: ServiceDatabaseResource
    ) -> dict[str, Output[str]]:
        return self.root.build_envs(database_resource)
