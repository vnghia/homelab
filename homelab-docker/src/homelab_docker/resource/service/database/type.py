from __future__ import annotations

import typing

import pulumi_docker as docker
import pulumi_random as random
from pulumi import ComponentResource, ResourceOptions
from pydantic import PositiveInt

from ....config.database import DatabaseConfig
from ....model.container import ContainerModel, ContainerModelBuildArgs
from ....model.container.database.source import ContainerDatabaseSourceModel
from ....model.container.extract import ContainerExtract
from ....model.container.extract.source import ContainerExtractSource
from ....model.container.extract.source.simple import (
    ContainerExtractSimpleSource,
)
from ....model.container.extract.source.volume import (
    ContainerExtractVolumeSource,
)
from ....model.container.image import ContainerImageModelConfig
from ....model.container.volume import (
    ContainerVolumeConfig,
    ContainerVolumesConfig,
)
from ....model.database.type import DatabaseType
from ....model.service.database import ServiceDatabaseModel

if typing.TYPE_CHECKING:
    from ...service import ServiceResourceBase


class ServiceDatabaseTypeResource(ComponentResource):
    PASSWORD_LENGTH = 64

    def __init__(
        self,
        type_: DatabaseType,
        model: ServiceDatabaseModel,
        *,
        opts: ResourceOptions,
        database_config: DatabaseConfig,
        main_service: ServiceResourceBase,
        name: str | None,
    ) -> None:
        self.type = type_
        self.config = database_config.root[self.type]
        self.model = model
        self.name = name

        super().__init__(type_, self.short_name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.service_name = main_service.name()
        self.username = self.service_name
        self.password = random.RandomPassword(
            self.short_name,
            opts=self.child_opts,
            length=self.PASSWORD_LENGTH,
            special=False,
        )
        self.database = self.service_name

        self.containers: dict[PositiveInt, docker.Container] = {}
        self.versions = self.config.get_versions(self.model)
        for version in self.versions:
            full_name = self.get_full_name_version(version)
            container = self.config.container.model_merge(
                ContainerModel(
                    image=ContainerImageModelConfig(
                        self.get_short_name_version(version)
                    ),
                    volumes=ContainerVolumesConfig(
                        {full_name: ContainerVolumeConfig(self.config.data_dir)}
                    ),
                    envs={
                        self.config.env.username: ContainerExtract(
                            ContainerExtractSource(
                                ContainerExtractSimpleSource(self.username)
                            )
                        ),
                        self.config.env.database: ContainerExtract(
                            ContainerExtractSource(
                                ContainerExtractSimpleSource(self.database)
                            )
                        ),
                        self.config.env.data_dir: ContainerExtract(
                            ContainerExtractSource(
                                ContainerExtractVolumeSource(volume=full_name)
                            )
                        ),
                    },
                )
            ).build_resource(
                full_name,
                opts=self.child_opts,
                main_service=main_service,
                build_args=ContainerModelBuildArgs(
                    envs={self.config.env.password: self.password.result}
                ),
            )
            self.containers[version] = container

        self.register_outputs({})

    @property
    def short_name(self) -> str:
        return self.type.get_short_name(self.name)

    def get_short_name_version(self, version: PositiveInt) -> str:
        return self.type.get_short_name_version(self.name, version)

    def get_full_name_version(self, version: PositiveInt) -> str:
        return self.type.get_full_name_version(self.service_name, self.name, version)

    def to_source_model(self, version: PositiveInt) -> ContainerDatabaseSourceModel:
        return ContainerDatabaseSourceModel(
            username=self.username,
            password=self.password.result,
            database=self.database,
            host=self.get_full_name_version(version),
            port=self.config.port,
        )
