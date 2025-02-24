from __future__ import annotations

import typing

import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from ...config.database import DatabaseConfig
from ...config.database.source import DatabaseSourceConfig
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
            for name, model in model.postgres.items()
        }

    @property
    def containers(self) -> dict[str, docker.Container]:
        return {
            resource.get_short_name_version(version): container
            for resource in self.postgres.values()
            for version, container in resource.containers.items()
        }

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
