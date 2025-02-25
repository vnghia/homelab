from __future__ import annotations

import typing

import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions
from pydantic import PositiveInt

from ...config.database import DatabaseConfig
from ...config.database.source import DatabaseSourceConfig
from ...model.database.type import DatabaseType
from .postgres import PostgresDatabaseResource

if typing.TYPE_CHECKING:
    from ..service import ServiceResourceBase


class DatabaseResource(ComponentResource):
    RESOURCE_NAME = "database"

    def __init__(
        self,
        model: DatabaseConfig,
        *,
        opts: ResourceOptions,
        main_service: ServiceResourceBase,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, main_service.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.postgres = {
            name: PostgresDatabaseResource(
                model, opts=self.child_opts, main_service=main_service, name=name
            )
            for name, model in model.root[DatabaseType.POSTGRES].items()
        }

    @property
    def containers(self) -> dict[str | None, dict[PositiveInt, docker.Container]]:
        return {name: versions.containers for name, versions in self.postgres.items()}

    @property
    def source_config(self) -> DatabaseSourceConfig:
        return DatabaseSourceConfig(
            postgres={
                name: {
                    version: resource.to_source_model(version)
                    for version in resource.model.versions
                }
                for name, resource in self.postgres.items()
            }
        )
