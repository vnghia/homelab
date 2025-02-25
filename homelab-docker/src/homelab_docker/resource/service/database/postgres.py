from __future__ import annotations

import typing

import pulumi_docker as docker
import pulumi_random as random
from pulumi import ComponentResource, ResourceOptions
from pydantic import PositiveInt

from ....model.container import ContainerModel, ContainerModelBuildArgs
from ....model.container.database.source import ContainerDatabaseSourceModel
from ....model.container.extract import ContainerExtract
from ....model.container.extract.source import ContainerExtractSource
from ....model.container.extract.source.simple import ContainerExtractSimpleSource
from ....model.container.extract.source.volume import ContainerExtractVolumeSource
from ....model.container.healthcheck import ContainerHealthCheckConfig
from ....model.container.image import ContainerImageModelConfig
from ....model.container.tmpfs import ContainerTmpfsConfig
from ....model.container.volume import (
    ContainerVolumeConfig,
    ContainerVolumeFullConfig,
    ContainerVolumesConfig,
)
from ....model.service.database.postgres import ServicePostgresDatabaseModel

if typing.TYPE_CHECKING:
    from ...service import ServiceResourceBase


class ServicePostgresDatabaseResource(ComponentResource):
    def __init__(
        self,
        model: ServicePostgresDatabaseModel,
        *,
        opts: ResourceOptions,
        main_service: ServiceResourceBase,
        name: str | None,
    ) -> None:
        self.model = model
        self.name = name

        super().__init__(model.DATABASE_TYPE, self.short_name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.service_name = main_service.name()

        self.username = self.model.username or self.service_name
        self.password = random.RandomPassword(
            self.short_name,
            opts=self.child_opts,
            length=self.model.PASSWORD_LENGTH,
            special=False,
        )
        self.database = self.model.database or self.service_name

        self.containers: dict[PositiveInt, docker.Container] = {}
        for version in self.model.versions:
            full_name = self.get_full_name_version(version)
            container = ContainerModel(
                image=ContainerImageModelConfig(
                    self.model.DATABASE_TYPE.get_short_name_version(None, version)
                ),
                healthcheck=ContainerHealthCheckConfig(
                    tests=[
                        ContainerExtract(
                            ContainerExtractSource(ContainerExtractSimpleSource(test))
                        )
                        for test in ["CMD", "pg_isready", "-U", self.database]
                    ],
                    interval="5s",
                    timeout="5s",
                    retries=5,
                ),
                network=model.network,
                tmpfs=[ContainerTmpfsConfig(self.model.PGRUN_PATH)],
                volumes=ContainerVolumesConfig(
                    {
                        full_name: ContainerVolumeConfig(self.model.PGDATA_PATH),
                        self.model.DATABASE_ENTRYPOINT_INITDB_VOLUME: ContainerVolumeConfig(
                            ContainerVolumeFullConfig(
                                path=self.model.DATABASE_ENTRYPOINT_INITDB_PATH,
                                read_only=True,
                            )
                        ),
                    }
                ),
                envs={
                    "POSTGRES_USER": ContainerExtract(
                        ContainerExtractSource(
                            ContainerExtractSimpleSource(self.username)
                        )
                    ),
                    "POSTGRES_DB": ContainerExtract(
                        ContainerExtractSource(
                            ContainerExtractSimpleSource(self.database)
                        )
                    ),
                    "PGDATA": ContainerExtract(
                        ContainerExtractSource(
                            ContainerExtractVolumeSource(volume=full_name)
                        )
                    ),
                },
            ).build_resource(
                full_name,
                opts=self.child_opts,
                main_service=main_service,
                build_args=ContainerModelBuildArgs(
                    envs={
                        "POSTGRES_PASSWORD": self.password.result,
                    }
                ),
            )
            self.containers[version] = container

        self.register_outputs({})

    @property
    def short_name(self) -> str:
        return self.model.DATABASE_TYPE.get_short_name(self.name)

    def get_short_name_version(self, version: PositiveInt) -> str:
        return self.model.DATABASE_TYPE.get_short_name_version(self.name, version)

    def get_full_name_version(self, version: PositiveInt) -> str:
        return self.model.DATABASE_TYPE.get_full_name_version(
            self.service_name, self.name, version
        )

    def to_source_model(self, version: PositiveInt) -> ContainerDatabaseSourceModel:
        return ContainerDatabaseSourceModel(
            username=self.username,
            password=self.password.result,
            database=self.database,
            host=self.get_full_name_version(version),
            port=self.model.PORT,
        )
