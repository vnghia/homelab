from __future__ import annotations

import typing

from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container.database.source import (
    ContainerDatabaseSourceModel,
)
from homelab_docker.model.service.database import ServiceDatabaseConfigModel
from homelab_docker.model.service.database.postgres import (
    ServiceDatabasePostgresConfigModel,
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
        self.name = resource_name

        minimum_redundancy = None
        last_backup_maximum_age = None
        retention_policy = None

        if database_config_model:
            if not isinstance(
                database_config_model.root, ServiceDatabasePostgresConfigModel
            ):
                raise TypeError("Service database config model is not Postgres config")

            backup_config = database_config_model.root.backup
            if backup_config:
                minimum_redundancy = backup_config.minimum_redundancy
                last_backup_maximum_age = backup_config.last_backup_maximum_age
                retention_policy = backup_config.retention_policy

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
                    "minimum_redundancy": str(
                        minimum_redundancy or barman_config.minimum_redundancy
                    ),
                    "last_backup_maximum_age": last_backup_maximum_age
                    or barman_config.last_backup_maximum_age,
                    "retention_policy": retention_policy
                    or barman_config.retention_policy,
                    "local_staging_path": GlobalExtractor(
                        barman_config.staging_dir
                    ).extract_path(barman_service.extractor_args),
                }
            },
            extractor_args=barman_service.extractor_args,
        )
