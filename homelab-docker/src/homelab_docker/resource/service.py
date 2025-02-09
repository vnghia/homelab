import pulumi
import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions
from pydantic.alias_generators import to_snake

from homelab_docker.config.database.source import DatabaseSourceConfig
from homelab_docker.model.container.model import (
    ContainerModel,
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
    ContainerModelServiceArgs,
)
from homelab_docker.model.service import ServiceModel

from .database.resource import DatabaseResource


class ServiceResourceBase[T](ComponentResource):
    CONTAINERS: dict[str, docker.Container] = {}
    DATABASE_SOURCE_CONFIGS: dict[str, DatabaseSourceConfig] = {}

    def __init__(
        self,
        model: ServiceModel[T],
        *,
        opts: ResourceOptions | None,
        container_model_global_args: ContainerModelGlobalArgs,
    ) -> None:
        super().__init__("{}-service".format(self.name()), self.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.model = model
        self.container_model_global_args = container_model_global_args
        self.build_databases()

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Service")).replace("_", "-")

    @property
    def config(self) -> T:
        return self.model.config

    def add_service_name(self, name: str | None) -> str:
        return "{}-{}".format(self.name(), name) if name else self.name()

    def build_databases(self) -> None:
        self.database = DatabaseResource(
            self.model.databases,
            opts=self.child_opts,
            service_name=self.name(),
            container_model_global_args=self.container_model_global_args,
        )

        self.container_model_service_args = ContainerModelServiceArgs(
            database_config=self.model.databases,
            database_source_config=self.database.source_config,
        )
        self.DATABASE_SOURCE_CONFIGS[self.name()] = (
            self.container_model_service_args.database_source_config
        )

        self.database_containers = {
            name: container for name, container in self.database.containers.items()
        }
        for name, container in self.database_containers.items():
            name = self.add_service_name(name)
            self.CONTAINERS[name] = container
            pulumi.export("container.{}".format(name), container.name)

    def build_container(
        self,
        name: str | None,
        model: ContainerModel,
        container_model_build_args: ContainerModelBuildArgs | None,
    ) -> docker.Container:
        container_model_build_args = (
            container_model_build_args or ContainerModelBuildArgs()
        )
        return model.build_resource(
            self.add_service_name(name),
            opts=self.child_opts,
            service_name=self.name(),
            global_args=self.container_model_global_args,
            service_args=self.container_model_service_args,
            build_args=container_model_build_args,
            containers=self.CONTAINERS,
        )

    def build_containers(
        self, options: dict[str | None, ContainerModelBuildArgs]
    ) -> None:
        self.containers = {
            name: self.build_container(name, model, options.get(name))
            for name, model in self.model.containers.items()
        } | (
            {
                None: self.build_container(
                    None, self.model.raw_container, options.get(None)
                )
            }
            if self.model.raw_container
            else {}
        )

        for name, container in self.containers.items():
            name = self.add_service_name(name)
            self.CONTAINERS[name] = container
            pulumi.export("container.{}".format(name), container.name)
