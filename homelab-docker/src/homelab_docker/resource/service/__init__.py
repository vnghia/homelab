from __future__ import annotations

from collections import defaultdict

import pulumi
import pulumi_tls as tls
from homelab_pydantic import HomelabBaseModel
from pulumi import ComponentResource, Output, ResourceOptions
from pydantic.alias_generators import to_snake

from ...extract import ExtractorArgs
from ...model.docker.container import ContainerModel, ContainerModelBuildArgs
from ...model.service import ServiceModel, ServiceWithConfigModel
from ..docker.container import ContainerResource
from ..file import FileResource
from .database import ServiceDatabaseResource
from .keepass import ServiceKeepassResource
from .secret import ServiceSecretResource


class ServiceResourceBase(ComponentResource):
    def __init__(
        self,
        model: ServiceModel,
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__("{}-service".format(self.name()), self.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.model = model

        self._database: ServiceDatabaseResource | None = None
        self._secret: ServiceSecretResource | None = None
        self._keepass: ServiceKeepassResource | None = None

        self.exports: dict[str, Output[str]] = {}
        self.containers: dict[str | None, ContainerResource] = {}
        self.extractor_args = extractor_args.from_service(self)

        self.build_databases()
        self.build_secrets()
        self.build_keepasses()

        self.options: defaultdict[str | None, ContainerModelBuildArgs] = defaultdict(
            ContainerModelBuildArgs
        )

        self.extractor_args.services[self.name()] = self

    def extractor_args_from_self(self, container: str | None) -> ExtractorArgs:
        return self.extractor_args.from_service(self, container)

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Service")).replace("_", "-")

    @classmethod
    def add_service_name(cls, name: str | None, prefix: str | None = None) -> str:
        return ServiceModel.add_service_name(prefix or cls.name(), name)

    @classmethod
    def get_key(cls, name: str | None) -> str | None:
        return None if name == cls.name() else name

    @property
    def container(self) -> ContainerResource:
        return self.containers[None]

    @property
    def database(self) -> ServiceDatabaseResource:
        if not self._database:
            raise ValueError(
                "{} service is not configured with database".format(self.name())
            )
        return self._database

    @property
    def secret(self) -> ServiceSecretResource:
        if not self._secret:
            raise ValueError(
                "{} service is not configured with secret".format(self.name())
            )
        return self._secret

    @property
    def keepass(self) -> ServiceKeepassResource:
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
                database_config=self.extractor_args.host_model.docker.database,
                extractor_args=self.extractor_args,
            )

            for type_, containers in self._database.containers.items():
                for name, versions in containers.items():
                    for version, container in versions.items():
                        pulumi.export(
                            "{}.container.{}".format(
                                self.extractor_args.host.name(),
                                type_.get_full_name_version(self.name(), name, version),
                            ),
                            container.name,
                        )

    def build_secrets(self) -> None:
        if self.model.secrets:
            self._secret = ServiceSecretResource(
                self.model.secrets, opts=self.child_opts, main_service=self
            )

            for name, secret in self._secret.secrets.secrets.items():
                if isinstance(secret, tls.PrivateKey):
                    pulumi.export(
                        "{}.secret.{}.private-key".format(
                            self.extractor_args.host.name(),
                            self.add_service_name(name),
                        ),
                        secret.private_key_openssh,
                    )
                    pulumi.export(
                        "{}.secret.{}.public-key".format(
                            self.extractor_args.host.name(),
                            self.add_service_name(name),
                        ),
                        secret.public_key_openssh,
                    )
                elif isinstance(secret, (tls.LocallySignedCert, tls.SelfSignedCert)):
                    pulumi.export(
                        "{}.secret.{}.cert".format(
                            self.extractor_args.host.name(),
                            self.add_service_name(name),
                        ),
                        secret.cert_pem,
                    )
                else:
                    pulumi.export(
                        "{}.secret.{}".format(
                            self.extractor_args.host.name(),
                            self.add_service_name(name),
                        ),
                        secret.result,
                    )

    def build_keepasses(self) -> None:
        if self.model.keepasses:
            self._keepass = ServiceKeepassResource(
                self.model.keepasses,
                opts=self.child_opts,
                extractor_args=self.extractor_args,
            )

    def build_container(
        self,
        name: str | None,
        model: ContainerModel,
        container_model_build_args: ContainerModelBuildArgs | None,
    ) -> ContainerResource:
        resource = model.build_resource(
            self.add_service_name(name),
            opts=self.child_opts,
            extractor_args=self.extractor_args,
            build_args=container_model_build_args,
        )
        return ContainerResource(model=model, resource=resource)

    def build_containers(self) -> None:
        from ...extract.global_ import GlobalExtractor

        if self.model.files:
            for name, config in self.model.files.root.items():
                extractor_args = self.extractor_args_from_self(name)
                files = []
                for file_resource_name, file_model in config.items():
                    if file_model.active:
                        file = FileResource(
                            file_resource_name,
                            opts=self.child_opts,
                            volume_path=GlobalExtractor(
                                file_model.path
                            ).extract_volume_path(extractor_args),
                            content=GlobalExtractor(file_model.content).extract_str(
                                extractor_args
                            ),
                            mode=file_model.mode,
                            extractor_args=self.extractor_args,
                        )
                        if file_model.bind:
                            files.append(file)
                if files:
                    self.options[name].files = [*self.options[name].files, *files]

        for name, model in self.model.containers.items():
            if model.active:
                self.containers[name] = self.build_container(
                    name, model.to_full(self.extractor_args), self.options.get(name)
                )
                if name is None:
                    self.extractor_args = self.extractor_args.from_service(self)

        for name, container in self.containers.items():
            pulumi.export(
                "{}.container.{}".format(
                    self.extractor_args.host.name(),
                    self.add_service_name(name),
                ),
                container.name,
            )


class ServiceWithConfigResourceBase[T: HomelabBaseModel](ServiceResourceBase):
    def __init__(
        self,
        model: ServiceWithConfigModel[T],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)
        self.config = model.config
