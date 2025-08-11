from __future__ import annotations

import typing
from pathlib import PosixPath

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_extract.container import ContainerExtract
from homelab_extract.container.volume import ContainerExtractVolumeSource
from homelab_extract.host import HostExtract
from homelab_extract.service import ServiceExtract
from homelab_pydantic import RelativePath
from homelab_secret.model.password import SecretPasswordModel
from pulumi import ComponentResource, ResourceOptions
from pydantic import PositiveInt

from ....config.docker.database import DatabaseConfig, DatabaseTypeEnvConfig
from ....extract import ExtractorArgs
from ....model.database.type import DatabaseType
from ....model.docker.container import ContainerModel, ContainerModelBuildArgs
from ....model.docker.container.database.source import ContainerDatabaseSourceModel
from ....model.docker.container.image import ContainerImageModelConfig
from ....model.docker.container.volume import (
    ContainerVolumeConfig,
    ContainerVolumeFullConfig,
    ContainerVolumesConfig,
)
from ....model.docker.container.volume_path import ContainerVolumePath
from ....model.service.database import ServiceDatabaseConfigModel, ServiceDatabaseModel
from ...file import FileResource

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class ServiceDatabaseTypeResource(ComponentResource):
    def __init__(
        self,
        type_: DatabaseType,
        model: ServiceDatabaseModel,
        *,
        opts: ResourceOptions,
        database_config: DatabaseConfig,
        extractor_args: ExtractorArgs,
        name: str | None,
    ) -> None:
        self.type = type_
        self.config = database_config.root[self.type]
        self.model = model
        self.name = name

        super().__init__(type_, self.short_name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.service_name = extractor_args.service.name()
        self.username = self.service_name
        self.password = SecretPasswordModel(special=False).build_resource(
            self.short_name, opts=self.child_opts
        )
        self.database = self.service_name

        self.superuser_password = None
        superuser_password_env = {}
        if self.config.env.superuser_password:
            self.superuser_password = SecretPasswordModel(special=False).build_resource(
                "superuser-{}".format(self.short_name), opts=self.child_opts
            )
            superuser_password_env[self.config.env.superuser_password] = (
                self.superuser_password.result
            )

        self.scripts = [
            FileResource(
                self.prefix + script.path,
                opts=self.child_opts,
                volume_path=ContainerVolumePath(
                    volume=self.full_name_initdb,
                    path=RelativePath(PosixPath("{:02}-{}".format(i, script.path))),
                ),
                content=script.content,
                mode=0o777,
                extractor_args=extractor_args,
            )
            for i, script in enumerate(self.config.scripts + model.scripts)
        ]

        self.containers: dict[PositiveInt, docker.Container] = {}
        self.versions: list[PositiveInt] = self.config.get_versions(self.model)
        for version in self.versions:
            full_name = self.get_full_name_version(version)
            container_model = self.config.container
            image_container_model = self.config.images[self.model.image][
                version
            ].container
            if image_container_model:
                container_model = container_model.model_merge(image_container_model)
            container = container_model.model_merge(
                ContainerModel(
                    image=ContainerImageModelConfig(
                        self.type.get_short_name_version(self.model.image, version)
                    ),
                    volumes=ContainerVolumesConfig(
                        {
                            full_name: ContainerVolumeConfig(
                                GlobalExtract.from_simple(
                                    self.config.data_dir.as_posix()
                                )
                            )
                        }
                        | (
                            {
                                self.get_full_name_version_tmp(
                                    version
                                ): ContainerVolumeConfig(
                                    GlobalExtract.from_simple(
                                        self.config.tmp_dir.as_posix()
                                    )
                                )
                            }
                            if self.config.tmp_dir
                            else {}
                        )
                        | (
                            {
                                self.full_name_initdb: ContainerVolumeConfig(
                                    ContainerVolumeFullConfig(
                                        path=GlobalExtract.from_simple(
                                            self.config.initdb_dir.as_posix()
                                        ),
                                        read_only=True,
                                    )
                                )
                            }
                            if self.config.initdb_dir
                            else {}
                        )
                    ),
                    envs={
                        self.config.env.database: GlobalExtract.from_simple(
                            self.database
                        ),
                        self.config.env.data_dir: GlobalExtract(
                            HostExtract(
                                ServiceExtract(
                                    ContainerExtract(
                                        ContainerExtractVolumeSource(volume=full_name)
                                    )
                                )
                            )
                        ),
                    }
                    | (
                        {
                            self.config.env.username: GlobalExtract.from_simple(
                                self.username
                            )
                        }
                        if self.config.env.username
                        else {}
                    ),
                )
            ).build_resource(
                full_name,
                opts=self.child_opts,
                extractor_args=extractor_args,
                build_args=ContainerModelBuildArgs(
                    envs={self.config.env.password: self.password.result}
                    | superuser_password_env,
                    files=self.scripts,
                ),
            )
            self.containers[version] = container

        self.register_outputs({})

    @property
    def prefix(self) -> str:
        return "{}-".format(self.name) if self.name else ""

    @property
    def short_name(self) -> str:
        return self.type.get_short_name(self.name)

    @property
    def full_name_initdb(self) -> str:
        return self.type.get_full_name_initdb(self.service_name, self.name)

    def get_short_name_version(self, version: PositiveInt) -> str:
        return self.type.get_short_name_version(self.name, version)

    def get_full_name_version(self, version: PositiveInt) -> str:
        return self.type.get_full_name_version(self.service_name, self.name, version)

    def get_full_name_version_tmp(self, version: PositiveInt) -> str:
        return self.type.get_full_name_version_tmp(
            self.service_name, self.name, version
        )

    def to_source_model(self, version: PositiveInt) -> ContainerDatabaseSourceModel:
        return ContainerDatabaseSourceModel(
            username=self.username
            if self.config.env.username
            else DatabaseTypeEnvConfig.DEFAULT_USERNAME,
            password=self.password.result,
            database=self.database,
            host=self.get_full_name_version(version),
            port=self.config.port,
            superuser_password=self.superuser_password.result
            if self.superuser_password
            else None,
        )

    def to_source_model_and_config(
        self, version: PositiveInt
    ) -> tuple[ContainerDatabaseSourceModel, ServiceDatabaseConfigModel | None]:
        return (self.to_source_model(version), self.model.config)
