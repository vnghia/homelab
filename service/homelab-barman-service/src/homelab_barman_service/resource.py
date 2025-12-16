from __future__ import annotations

import typing
from typing import cast

from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container.database.source import (
    ContainerDatabaseSourceModel,
)
from homelab_docker.model.service.database import ServiceDatabaseConfigModel
from homelab_docker.model.service.database.postgres import (
    ServiceDatabasePostgresConfigModel,
)
from homelab_docker.model.service.database.postgres.backup import (
    ServiceDatabasePostgresBackupConfigModel,
)
from homelab_docker.resource.file.config import (
    ConfigFileResource,
    IniDumper,
    JsonDefaultModel,
)
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from . import BarmanService


class BarmanConfigFileResource(
    ConfigFileResource[JsonDefaultModel], module="barman", name="Config"
):
    validator = JsonDefaultModel
    dumper = IniDumper[JsonDefaultModel]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        database_source_model: ContainerDatabaseSourceModel,
        database_config_model: ServiceDatabaseConfigModel | None,
        barman_service: BarmanService,
    ) -> None:
        barman_config = barman_service.config
        backup_config = cast(ServiceDatabasePostgresBackupConfigModel, barman_config)
        self.name = resource_name

        if database_config_model:
            if not isinstance(
                database_config_model.root, ServiceDatabasePostgresConfigModel
            ):
                raise TypeError("Service database config model is not Postgres config")

            if database_config_model.root.backup:
                backup_config = backup_config.model_merge(
                    database_config_model.root.backup
                )

        super().__init__(
            self.name,
            opts=opts,
            volume_path=barman_service.get_config_volume_path(self.name),
            data={
                self.name: {
                    "description": self.name,
                    "conninfo": database_source_model.to_kv({"sslmode": "disable"}),
                    "backup_method": "postgres",
                    "archiver": "off",
                    "streaming_archiver": "on",
                    "slot_name": barman_service.name(),
                    "create_slot": "auto",
                    "local_staging_path": GlobalExtractor(
                        barman_config.staging_dir
                    ).extract_path(barman_service.extractor_args),
                }
                | (
                    {"minimum_redundancy": str(backup_config.minimum_redundancy)}
                    if backup_config.minimum_redundancy
                    else {}
                )
                | (
                    {"last_backup_maximum_age": backup_config.last_backup_maximum_age}
                    if backup_config.last_backup_maximum_age
                    else {}
                )
                | (
                    {"retention_policy": backup_config.retention_policy}
                    if backup_config.retention_policy
                    else {}
                )
                | (
                    {"backup_compression": backup_config.backup_compression}
                    if backup_config.backup_compression
                    else {}
                )
                | (
                    {
                        "backup_compression_level": str(
                            backup_config.backup_compression_level
                        )
                    }
                    if backup_config.backup_compression_level
                    else {}
                )
                | (
                    {"compression": backup_config.compression}
                    if backup_config.compression
                    else {}
                )
            },
            permission=barman_service.user,
            extractor_args=barman_service.extractor_args,
        )
