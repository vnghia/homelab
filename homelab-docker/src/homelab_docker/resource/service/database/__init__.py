from __future__ import annotations

import typing

import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions
from pydantic import PositiveInt

from ....config.docker.database import DatabaseConfig
from ....config.service.database import ServiceDatabaseConfig
from ....config.service.database.source import ServiceDatabaseSourceConfig
from ....model.database.type import DatabaseType
from .type import ServiceDatabaseTypeResource

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class ServiceDatabaseContainers(
    dict[DatabaseType, dict[str | None, dict[PositiveInt, docker.Container]]]
):
    pass


class ServiceDatabaseResource(ComponentResource):
    RESOURCE_NAME = "database"

    def __init__(
        self,
        config: ServiceDatabaseConfig,
        *,
        opts: ResourceOptions,
        database_config: DatabaseConfig,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, extractor_args.service.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config
        self.resources = {
            type_: {
                name: ServiceDatabaseTypeResource(
                    type_,
                    model,
                    opts=self.child_opts,
                    database_config=database_config,
                    extractor_args=extractor_args,
                    name=name,
                )
                for name, model in config.items()
            }
            for type_, config in self.config.root.items()
        }

        self.containers = ServiceDatabaseContainers(
            {
                type_: {
                    name: resource.containers for name, resource in resources.items()
                }
                for type_, resources in self.resources.items()
            }
        )
        self.source_config = ServiceDatabaseSourceConfig(
            {
                type_: {
                    name: {
                        version: resource.to_source_model_and_config(version)
                        for version in resource.versions
                    }
                    for name, resource in resources.items()
                }
                for type_, resources in self.resources.items()
            }
        )

        self.register_outputs({})
