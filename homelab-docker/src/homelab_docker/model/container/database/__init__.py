from __future__ import annotations

import typing

import pulumi_docker as docker
from homelab_pydantic import HomelabRootModel
from pulumi import Output
from pydantic import PositiveInt

from .mysql import ContainerDatabaseMysqlConfig
from .postgres import ContainerDatabasePostgresConfig
from .redis import ContainerDatabaseRedisConfig

if typing.TYPE_CHECKING:
    from ....resource.service.database import ServiceDatabaseResource


class ContainerDatabaseConfig(
    HomelabRootModel[
        ContainerDatabaseMysqlConfig
        | ContainerDatabasePostgresConfig
        | ContainerDatabaseRedisConfig
    ]
):
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
