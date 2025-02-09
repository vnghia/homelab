from homelab_backup_service.config.barman import BarmanConfig
from homelab_docker.config.database.source import DatabaseSourceConfig
from homelab_docker.model.container.model import ContainerModel
from homelab_docker.model.database.postgres import PostgresDatabaseModel
from homelab_docker.model.file.config import ConfigFile
from homelab_docker.resource.volume import VolumeResource
from pulumi import ComponentResource, ResourceOptions


class BarmanResource(ComponentResource):
    RESOURCE_NAME = "barman"

    def __init__(
        self,
        config: BarmanConfig,
        *,
        opts: ResourceOptions,
        container_model: ContainerModel,
        database_source_configs: dict[str, DatabaseSourceConfig],
        volume_resource: VolumeResource,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        for service_name, source_config in database_source_configs.items():
            for name, sources in source_config.postgres.items():
                for version, source in sources.items():
                    full_name = PostgresDatabaseModel.get_full_name_version(
                        service_name, name, version
                    )
                    ConfigFile(
                        container_volume_path=config.get_config_container_volume_path(
                            full_name
                        ),
                        data={
                            full_name: {
                                "description": full_name,
                                "conninfo": source.to_kv({"sslmode": "disable"}),
                                "backup_method": "postgres",
                                "archiver": "off",
                                "streaming_archiver": "on",
                                "slot_name": "barman",
                                "create_slot": "auto",
                                "minimum_redundancy": str(config.minimum_redundancy),
                                "retention_policy": config.retention_policy,
                                "local_staging_path": config.staging_dir.to_container_path(
                                    container_model.volumes
                                ).as_posix(),
                            }
                        },
                    ).build_resource(
                        full_name, opts=self.child_opts, volume_resource=volume_resource
                    )
