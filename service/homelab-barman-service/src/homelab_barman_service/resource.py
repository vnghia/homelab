from __future__ import annotations

import typing

from homelab_docker.model.database.source import DatabaseSourceModel
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
        opts: ResourceOptions | None,
        database_source_model: DatabaseSourceModel,
        barman_service: BarmanService,
    ):
        barman_config = barman_service.config

        super().__init__(
            resource_name,
            opts=opts,
            volume_path=barman_service.get_config_volume_path(resource_name),
            data={
                resource_name: {
                    "description": resource_name,
                    "conninfo": database_source_model.to_kv({"sslmode": "disable"}),
                    "backup_method": "postgres",
                    "archiver": "off",
                    "streaming_archiver": "on",
                    "slot_name": barman_service.name(),
                    "create_slot": "auto",
                    "minimum_redundancy": str(barman_config.minimum_redundancy),
                    "last_backup_maximum_age": barman_config.last_backup_maximum_age,
                    "retention_policy": barman_config.retention_policy,
                    "local_staging_path": barman_config.staging_dir.extract_volume_path(
                        barman_service.model
                    ),
                }
            },
            volume_resource=barman_service.docker_resource_args.volume,
        )
