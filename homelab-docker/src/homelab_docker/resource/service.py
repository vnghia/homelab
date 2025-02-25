import dataclasses

import pulumi
import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pulumi import ComponentResource, ResourceOptions
from pydantic import PositiveInt
from pydantic.alias_generators import to_snake

from ..config.database import DatabaseConfig
from ..config.database.source import DatabaseSourceConfig
from ..model.container import ContainerModel, ContainerModelBuildArgs
from ..model.service import ServiceModel, ServiceWithConfigModel
from . import DockerResourceArgs
from .database import DatabaseResource


@dataclasses.dataclass
class ServiceDatabaseArgs:
    config: DatabaseConfig
    source_config: DatabaseSourceConfig
    containers: dict[str | None, dict[PositiveInt, docker.Container]]


class ServiceResourceBase(ComponentResource):
    CONTAINER_RESOURCE: dict[str, dict[str | None, docker.Container]] = {}
    DATABASE_SOURCE_CONFIGS: dict[str, DatabaseSourceConfig] = {}

    def __init__(
        self,
        model: ServiceModel,
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__("{}-service".format(self.name()), self.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.model = model
        self.docker_resource_args = docker_resource_args
        self.build_databases()

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Service")).replace("_", "-")

    @classmethod
    def add_service_name_cls(cls, service_name: str, name: str | None) -> str:
        return "{}-{}".format(service_name, name) if name else service_name

    def add_service_name(self, name: str | None) -> str:
        return self.add_service_name_cls(self.name(), name)

    def build_databases(self) -> None:
        self.database_args: ServiceDatabaseArgs | None = None
        if self.model.databases:
            database = DatabaseResource(
                self.model.databases, opts=self.child_opts, main_service=self
            )
            self.database_args = ServiceDatabaseArgs(
                config=self.model.databases,
                source_config=database.source_config,
                containers=database.containers,
            )
            self.DATABASE_SOURCE_CONFIGS[self.name()] = self.database_args.source_config

            for name, versions in self.database_args.containers.items():
                for version, container in versions.items():
                    name = self.add_service_name(name)
                    pulumi.export("container.{}".format(name), container.name)

    def build_container(
        self,
        name: str | None,
        model: ContainerModel,
        container_model_build_args: ContainerModelBuildArgs | None,
    ) -> docker.Container:
        return model.build_resource(
            self.add_service_name(name),
            opts=self.child_opts,
            main_service=self,
            build_args=container_model_build_args,
        )

    def build_containers(
        self, options: dict[str | None, ContainerModelBuildArgs]
    ) -> None:
        self.containers = {
            name: self.build_container(name, model, options.get(name))
            for name, model in self.model.containers.items()
            if model.active
        }

        self.CONTAINER_RESOURCE[self.name()] = {}
        for name, container in self.containers.items():
            self.CONTAINER_RESOURCE[self.name()][name] = container
            pulumi.export(
                "container.{}".format(self.add_service_name(name)), container.name
            )


class ServiceWithConfigResourceBase[T: HomelabBaseModel](ServiceResourceBase):
    def __init__(
        self,
        model: ServiceWithConfigModel[T],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)
        self.config = model.config
