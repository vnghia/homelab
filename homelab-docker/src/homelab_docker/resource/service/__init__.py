from __future__ import annotations

from collections import defaultdict

import pulumi
import pulumi_tls as tls
from homelab_extract.service.mtls import MTlsInfoSourceModel
from homelab_pydantic import HomelabBaseModel
from homelab_secret.resource import SecretResource
from homelab_secret.resource.cert.mtls import SecretMTlsResource
from pulumi import Alias, ComponentResource, Output, ResourceOptions
from pydantic.alias_generators import to_snake

from ...extract import ExtractorArgs
from ...model.docker.container import ContainerModel, ContainerModelBuildArgs
from ...model.docker.container.ports import ContainerPortsConfig
from ...model.file import FilePermissionModel
from ...model.service import ServiceModel, ServiceWithConfigModel
from ..docker.container import ContainerResource
from ..file import FileResource
from ..vpn import VpnModelBuilder
from .database import ServiceDatabaseResource
from .keepass import ServiceKeepassResource


class ServiceResourceBase(ComponentResource):
    _service_name: str | None = None

    def __init__(
        self,
        model: ServiceModel,
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        self.service_resource_name = "{}-service".format(self.name())

        self.aliases = []
        if model.old:
            from ...resource.host import HostResourceBase

            host_resource = extractor_args.get_host(model.old.host)
            if not isinstance(host_resource, HostResourceBase):
                raise ValueError("Old host must be initialized before moving")
            self.aliases.append(Alias(parent=host_resource))

        super().__init__(
            self.service_resource_name,
            self.name(),
            None,
            ResourceOptions.merge(opts, ResourceOptions(aliases=self.aliases)),
        )
        self.child_opts = ResourceOptions(parent=self)
        self.child_opts_no_aliases = ResourceOptions.merge(
            self.child_opts, ResourceOptions(aliases=[])
        )

        self.model = model
        self.user = extractor_args.host.service_users[self.name()]

        self._database: ServiceDatabaseResource | None = None
        self._secret: SecretResource | None = None
        self._keepass: ServiceKeepassResource | None = None

        self.exports: dict[str, Output[str] | list[Output[str]]] = {}
        self.container_models: dict[str | None, ContainerModel] = model.containers
        self.containers: dict[str | None, ContainerResource] = {}
        self.options: defaultdict[str | None, ContainerModelBuildArgs] = defaultdict(
            ContainerModelBuildArgs
        )

        self.extractor_args = extractor_args.from_service(self)
        self.extractor_args.services[self.name()] = self

        self.build_databases()
        self.build_secrets()
        self.build_keepasses()
        self.build_files()
        self.build_vpn_container_model()
        self.build_options_network()

    def extractor_args_from_self(self, container: str | None) -> ExtractorArgs:
        return self.extractor_args.from_service(self, container)

    @classmethod
    def name(cls) -> str:
        if cls._service_name is None:
            cls._service_name = to_snake(cls.__name__.removesuffix("Service")).replace(
                "_", "-"
            )
        return cls._service_name

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
    def secret(self) -> SecretResource:
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
        container_models: dict[str | None, ContainerModel] = {}
        if self.model.databases:
            self._database = ServiceDatabaseResource(
                self.model.databases,
                opts=self.child_opts,
                database_config=self.extractor_args.host_model.docker.database,
                extractor_args=self.extractor_args,
            )

            for containers in self._database.containers.values():
                for versions in containers.values():
                    for container in versions.values():
                        container_models[container.name] = container.model
                        self.options[container.name] = container.option
        self.container_models = container_models | self.container_models

    def build_secrets(self) -> None:
        if self.model.secrets:
            self._secret = SecretResource(
                self.model.secrets,
                opts=self.child_opts,
                name=self.name(),
                plain_args=self.extractor_args.plain_args,
            )

            for name, secret in self._secret.secrets.items():
                if isinstance(secret, tls.PrivateKey):
                    pulumi.export(
                        "{}.secret.{}.private-key".format(
                            self.extractor_args.host.name,
                            self.add_service_name(name),
                        ),
                        secret.private_key_openssh,
                    )
                    pulumi.export(
                        "{}.secret.{}.public-key".format(
                            self.extractor_args.host.name,
                            self.add_service_name(name),
                        ),
                        secret.public_key_openssh,
                    )
                elif isinstance(secret, (tls.LocallySignedCert, tls.SelfSignedCert)):
                    pulumi.export(
                        "{}.secret.{}.cert".format(
                            self.extractor_args.host.name,
                            self.add_service_name(name),
                        ),
                        secret.cert_pem,
                    )
                elif isinstance(secret, SecretMTlsResource):
                    for info in MTlsInfoSourceModel:
                        pulumi.export(
                            "{}.secret.{}.{}".format(
                                self.extractor_args.host.name,
                                self.add_service_name(name),
                                info.replace("_", "-"),
                            ),
                            secret.get_info(info),
                        )
                else:
                    pulumi.export(
                        "{}.secret.{}".format(
                            self.extractor_args.host.name,
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

    def build_files(self) -> None:
        from ...extract.global_ import GlobalExtractor

        if self.model.files:
            for file_resource_name, file_model in self.model.files.root.items():
                if not file_resource_name:
                    raise RuntimeError("File resource name is not valid")
                if file_model.active:
                    file = FileResource(
                        file_resource_name,
                        opts=self.child_opts,
                        volume_path=GlobalExtractor(
                            file_model.path
                        ).extract_volume_path(self.extractor_args),
                        content=GlobalExtractor(file_model.content).extract_str(
                            self.extractor_args
                        ),
                        permission=FilePermissionModel(
                            mode=file_model.mode, owner=self.user
                        ),
                        extractor_args=self.extractor_args,
                    )
                    if file_model.bind:
                        self.extractor_args.host.docker.volume.add_file(file)

    def build_vpn_container_model(self) -> None:
        if self.model.network.vpn:
            host_vpn_config = self.extractor_args.host_model.docker.network.vpn_
            vpn = self.model.network.vpn
            self.options[vpn.VPN_CONTAINER].add_envs(
                VpnModelBuilder(vpn.root).build_envs(self.extractor_args)
            )

            vpn_containers: dict[str | None, ContainerModel] = {
                vpn.VPN_CONTAINER: self.extractor_args.host_model.services[
                    host_vpn_config.service
                ][host_vpn_config.container].__replace__(
                    active=True, ports=ContainerPortsConfig(), wud=None
                )
            }
            self.container_models = vpn_containers | self.container_models

    def build_options_network(self) -> None:
        for name, network in self.extractor_args.host.docker.network.options[
            self.name()
        ].items():
            self.options[name].add_network(network)

    def build_container(
        self,
        name: str | None,
        model: ContainerModel,
        container_model_build_args: ContainerModelBuildArgs | None,
    ) -> ContainerResource:
        resource = model.build_resource(
            self.add_service_name(name),
            opts=self.child_opts_no_aliases,
            extractor_args=self.extractor_args,
            build_args=container_model_build_args,
        )
        return ContainerResource(key=name, model=model, resource=resource)

    def build_containers(self) -> None:
        for name, model in self.container_models.items():
            if model.active:
                self.containers[name] = self.build_container(
                    name, model.to_full(self.extractor_args), self.options.get(name)
                )
                if name is None:
                    self.extractor_args = self.extractor_args.from_service(self)

        for name, container in self.containers.items():
            pulumi.export(
                "{}.container.{}".format(
                    self.extractor_args.host.name,
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
