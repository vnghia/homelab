import pulumi
import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pulumi import ComponentResource, ResourceOptions
from pydantic.alias_generators import to_snake

from ...config.service.database.source import ServiceDatabaseSourceConfig
from ...model.container import ContainerModel, ContainerModelBuildArgs
from ...model.service import ServiceModel, ServiceWithConfigModel
from .. import DockerResourceArgs
from .database import ServiceDatabaseResource
from .secret import ServiceSecretResouse


class ServiceResourceBase(ComponentResource):
    CONTAINER_RESOURCE: dict[str, dict[str | None, docker.Container]] = {}
    DATABASE_SOURCE_CONFIGS: dict[str, ServiceDatabaseSourceConfig] = {}

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
        self.build_secrets()

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Service")).replace("_", "-")

    @classmethod
    def add_service_name(cls, name: str | None) -> str:
        return "{}-{}".format(cls.name(), name) if name else cls.name()

    @classmethod
    def get_key(cls, name: str | None) -> str | None:
        return None if name == cls.name() else name

    def build_databases(self) -> None:
        self.database: ServiceDatabaseResource | None = None
        if self.model.databases:
            self.database = ServiceDatabaseResource(
                self.model.databases,
                opts=self.child_opts,
                database_config=self.docker_resource_args.config.database,
                main_service=self,
            )
            self.DATABASE_SOURCE_CONFIGS[self.name()] = self.database.source_config

            for type_, containers in self.database.containers.items():
                for name, versions in containers.items():
                    for version, container in versions.items():
                        pulumi.export(
                            "container.{}".format(
                                type_.get_full_name_version(self.name(), name, version)
                            ),
                            container.name,
                        )

    def build_secrets(self) -> None:
        self.secret: ServiceSecretResouse | None = None
        if self.model.secrets:
            self.secret = ServiceSecretResouse(
                self.model.secrets, opts=self.child_opts, main_service=self
            )

            for name, secret in self.secret.secrets.items():
                pulumi.export(
                    "secret.{}".format(self.add_service_name(name)),
                    secret.result,
                )

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
