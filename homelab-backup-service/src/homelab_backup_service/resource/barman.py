from pathlib import PosixPath

import pulumi_docker as docker
from homelab_backup_service.config.barman import BarmanConfig
from homelab_dagu_service import DaguService
from homelab_dagu_service.dag import DaguDag, DaguDagStep
from homelab_docker.config.database.source import DatabaseSourceConfig
from homelab_docker.model.container.model import ContainerModel
from homelab_docker.model.database.postgres import PostgresDatabaseModel
from homelab_docker.model.file.config import ConfigFile
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.volume import VolumeResource
from pulumi import ComponentResource, ResourceOptions


class BarmanResource(ComponentResource):
    RESOURCE_NAME = "barman"
    SERVER_NAME_KEY = "SERVER_NAME"
    SERVER_NAME_DEFAULT_VALUE = "all"

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

        self.files: list[FileResource] = []
        for service_name, source_config in database_source_configs.items():
            for name, sources in source_config.postgres.items():
                for version, source in sources.items():
                    full_name = PostgresDatabaseModel.get_full_name_version(
                        service_name, name, version
                    )
                    file = ConfigFile(
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
                                "slot_name": self.RESOURCE_NAME,
                                "create_slot": "auto",
                                "minimum_redundancy": str(config.minimum_redundancy),
                                "retention_policy": config.retention_policy,
                                "local_staging_path": config.staging_dir.to_container_path(
                                    container_model.volumes
                                ).as_posix(),
                            }
                        },
                    ).build_resource(
                        full_name,
                        opts=self.child_opts,
                        volume_resource=volume_resource,
                    )
                    self.files.append(file)

    def build_dag_files(
        self,
        *,
        service_name: str,
        barman_container: docker.Container,
        dagu_service: DaguService,
        volume_resource: VolumeResource,
    ) -> None:
        executor = {
            "type": "docker",
            "config": {"containerName": barman_container.name},
        }

        # Run barman check manually
        # TODO: Use param after https://github.com/dagu-org/dagu/issues/827
        self.check_name = "{}-check".format(self.RESOURCE_NAME)
        self.check = DaguDag(
            path=PosixPath("{}-{}".format(service_name, self.check_name)),
            name=self.check_name,
            group=service_name,
            tags=[self.RESOURCE_NAME],
            params={self.SERVER_NAME_KEY: self.SERVER_NAME_DEFAULT_VALUE},
            steps=[
                DaguDagStep(
                    name="check", command="barman check all", executor=executor
                ),
            ],
        ).build_resource(
            "dagu-check",
            opts=self.child_opts,
            dagu_service=dagu_service,
            volume_resource=volume_resource,
        )

        # Run barman cron every minutes
        self.cron_name = "{}-cron".format(self.RESOURCE_NAME)
        self.cron = DaguDag(
            path=PosixPath("{}-{}".format(service_name, self.cron_name)),
            name=self.cron_name,
            group=service_name,
            tags=[self.RESOURCE_NAME],
            schedule="* * * * *",
            max_active_runs=1,
            steps=[
                DaguDagStep(
                    name="cron",
                    command="barman cron --keep-descriptors",
                    executor=executor,
                )
            ],
        ).build_resource(
            "dagu-cron",
            opts=self.child_opts,
            dagu_service=dagu_service,
            volume_resource=volume_resource,
        )
