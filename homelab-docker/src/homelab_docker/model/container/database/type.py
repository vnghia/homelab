from __future__ import annotations

import typing
from typing import ClassVar

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pulumi import Output
from pydantic import PositiveInt

from ...database.type import DatabaseType
from .source import (
    ContainerDatabaseSourceEnvsBase,
    ContainerDatabaseSourceEnvsRootBase,
    ContainerDatabaseSourceModel,
)

if typing.TYPE_CHECKING:
    from ....resource.service.database import ServiceDatabaseResource


class ContainerDatabaseTypeConfig[T: ContainerDatabaseSourceEnvsBase](HomelabBaseModel):
    TYPE: ClassVar[DatabaseType]

    name: str | None
    version: PositiveInt | None = None
    envs: ContainerDatabaseSourceEnvsRootBase[T] | None = None

    def to_database_version(
        self, database_resource: ServiceDatabaseResource
    ) -> PositiveInt:
        return (
            self.version
            or database_resource.resources[self.TYPE][self.name].versions[0]
        )

    def to_container(
        self, database_resource: ServiceDatabaseResource
    ) -> docker.Container:
        return database_resource.resources[self.TYPE][self.name].containers[
            self.to_database_version(database_resource)
        ]

    def to_container_name(self, database_resource: ServiceDatabaseResource) -> str:
        return database_resource.resources[self.TYPE][self.name].get_full_name_version(
            self.to_database_version(database_resource)
        )

    def to_database_source_model(
        self, database_resource: ServiceDatabaseResource
    ) -> ContainerDatabaseSourceModel:
        return database_resource.source_config[self.TYPE][self.name][
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
