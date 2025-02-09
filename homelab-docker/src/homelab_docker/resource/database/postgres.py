import pulumi_docker as docker
import pulumi_random as random
from pulumi import ComponentResource, ResourceOptions
from pydantic import PositiveInt

from homelab_docker.model.container.healthcheck import ContainerHealthCheckConfig
from homelab_docker.model.container.model import (
    ContainerModel,
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
)
from homelab_docker.model.container.string import ContainerString
from homelab_docker.model.container.tmpfs import ContainerTmpfsConfig
from homelab_docker.model.container.volume import (
    ContainerVolumeConfig,
    ContainerVolumeFullConfig,
    ContainerVolumesConfig,
)
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.database.postgres import PostgresDatabaseModel
from homelab_docker.model.database.source import DatabaseSourceModel


class PostgresDatabaseResource(ComponentResource):
    def __init__(
        self,
        model: PostgresDatabaseModel,
        *,
        opts: ResourceOptions,
        service_name: str,
        name: str | None,
        container_model_global_args: ContainerModelGlobalArgs,
    ) -> None:
        self.model = model
        self.name = name

        super().__init__(
            PostgresDatabaseModel.DATABASE_TYPE, self.short_name, None, opts
        )
        self.child_opts = ResourceOptions(parent=self)

        self.service_name = service_name

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
                image=self.model.get_short_name_version(None, version),
                healthcheck=ContainerHealthCheckConfig(
                    tests=["CMD", "pg_isready", "-U", self.database],
                    interval="5s",
                    timeout="5s",
                    retries=5,
                ),
                network=model.network,
                tmpfs=[ContainerTmpfsConfig(self.model.PGRUN_PATH)],
                volumes=ContainerVolumesConfig.model_validate(
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
                    "POSTGRES_USER": ContainerString(self.username),
                    "POSTGRES_DB": ContainerString(self.database),
                    "PGDATA": ContainerString(ContainerVolumePath(volume=full_name)),
                },
            ).build_resource(
                full_name,
                opts=self.child_opts,
                service_name=service_name,
                global_args=container_model_global_args,
                service_args=None,
                build_args=ContainerModelBuildArgs(
                    envs={
                        "POSTGRES_PASSWORD": self.password.result,
                    }
                ),
                containers={},
            )
            self.containers[version] = container

        self.register_outputs({})

    @property
    def short_name(self) -> str:
        return self.model.get_short_name(self.name)

    def get_short_name_version(self, version: PositiveInt) -> str:
        return self.model.get_short_name_version(self.name, version)

    def get_full_name_version(self, version: PositiveInt) -> str:
        return self.model.get_full_name_version(self.service_name, self.name, version)

    def to_source_model(self, version: PositiveInt) -> DatabaseSourceModel:
        return DatabaseSourceModel(
            username=self.username,
            password=self.password.result,
            database=self.database,
            host=self.get_full_name_version(version),
            port=self.model.PORT,
        )
