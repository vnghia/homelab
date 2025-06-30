from __future__ import annotations

from collections import defaultdict

import pulumi
import pulumi_docker as docker
import pulumi_tls as tls
from homelab_pydantic import HomelabBaseModel
from pulumi import ComponentResource, Output, ResourceOptions
from pydantic.alias_generators import to_snake

from ...config.service.database.source import ServiceDatabaseSourceConfig
from ...model.container import ContainerModel, ContainerModelBuildArgs
from ...model.service import ServiceModel, ServiceWithConfigModel
from .. import DockerResourceArgs
from .database import ServiceDatabaseResource
from .keepass import ServiceKeepassResouse
from .secret import ServiceSecretResouse


class ServiceResourceBase(ComponentResource):
    CONTAINER_RESOURCE: dict[str, dict[str | None, docker.Container]] = {}
    DATABASE_SOURCE_CONFIGS: dict[str, ServiceDatabaseSourceConfig] = {}
    SERVICES: dict[str, ServiceResourceBase] = {}

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

        self._database: ServiceDatabaseResource | None = None
        self._secret: ServiceSecretResouse | None = None
        self._keepass: ServiceKeepassResouse | None = None

        self.exports: dict[str, Output[str]] = {}

        self.build_databases()
        self.build_secrets()
        self.build_keepasses()

        self.options: defaultdict[str | None, ContainerModelBuildArgs] = defaultdict(
            ContainerModelBuildArgs
        )

        self.SERVICES[self.name()] = self

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Service")).replace("_", "-")

    @classmethod
    def add_service_name(cls, name: str | None, prefix: str | None = None) -> str:
        prefix = prefix or cls.name()
        return "{}-{}".format(prefix, name) if name else prefix

    @classmethod
    def get_key(cls, name: str | None) -> str | None:
        return None if name == cls.name() else name

    @property
    def container(self) -> docker.Container:
        return self.containers[None]

    @property
    def database(self) -> ServiceDatabaseResource:
        if not self._database:
            raise ValueError(
                "{} service is not configured with database".format(self.name())
            )
        return self._database

    @property
    def secret(self) -> ServiceSecretResouse:
        if not self._secret:
            raise ValueError(
                "{} service is not configured with secret".format(self.name())
            )
        return self._secret

    @property
    def keepass(self) -> ServiceKeepassResouse:
        if not self._keepass:
            raise ValueError(
                "{} service is not configured with keepass".format(self.name())
            )
        return self._keepass

    def build_databases(self) -> None:
        if self.model.databases:
            self._database = ServiceDatabaseResource(
                self.model.databases,
                opts=self.child_opts,
                database_config=self.docker_resource_args.config.database,
                main_service=self,
            )
            self.DATABASE_SOURCE_CONFIGS[self.name()] = self._database.source_config

            for type_, containers in self._database.containers.items():
                for name, versions in containers.items():
                    for version, container in versions.items():
                        pulumi.export(
                            "container.{}".format(
                                type_.get_full_name_version(self.name(), name, version)
                            ),
                            container.name,
                        )

    def build_secrets(self) -> None:
        if self.model.secrets:
            self._secret = ServiceSecretResouse(
                self.model.secrets, opts=self.child_opts, main_service=self
            )

            for name, secret in self._secret.secrets.items():
                if isinstance(secret, tls.PrivateKey):
                    pulumi.export(
                        "secret.{}.private-key".format(self.add_service_name(name)),
                        secret.private_key_openssh,
                    )
                    pulumi.export(
                        "secret.{}.public-key".format(self.add_service_name(name)),
                        secret.public_key_openssh,
                    )
                else:
                    pulumi.export(
                        "secret.{}".format(self.add_service_name(name)),
                        secret.result,
                    )

    def build_keepasses(self) -> None:
        if self.model.keepasses:
            self._keepass = ServiceKeepassResouse(
                self.model.keepasses, opts=self.child_opts, main_service=self
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

    def build_containers(self) -> None:
        self.containers = {
            name: self.build_container(name, model, self.options.get(name))
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
