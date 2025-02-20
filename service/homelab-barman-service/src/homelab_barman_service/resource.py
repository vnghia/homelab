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
        config = barman_service.config
        super().__init__(
            resource_name,
            opts=opts,
            container_volume_path=config.get_config_container_volume_path(
                resource_name
            ),
            data={
                resource_name: {
                    "description": resource_name,
                    "conninfo": database_source_model.to_kv({"sslmode": "disable"}),
                    "backup_method": "postgres",
                    "archiver": "off",
                    "streaming_archiver": "on",
                    "slot_name": barman_service.name(),
                    "create_slot": "auto",
                    "minimum_redundancy": str(config.minimum_redundancy),
                    "last_backup_maximum_age": config.last_backup_maximum_age,
                    "retention_policy": config.retention_policy,
                    "local_staging_path": config.staging_dir.to_container_path(
                        barman_service.model.container.volumes
                    ),
                }
            },
            volume_resource=barman_service.docker_resource_args.volume,
        )
