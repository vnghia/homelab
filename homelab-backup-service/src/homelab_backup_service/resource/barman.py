from pathlib import PosixPath

import pulumi_docker as docker
from homelab_dagu_service import DaguService
from homelab_dagu_service.config import DaguDagConfig
from homelab_dagu_service.config.executor.docker import DaguDagDockerExecutorConfig
from homelab_dagu_service.config.step import DaguDagStepConfig
from homelab_docker.config.database.source import DatabaseSourceConfig
from homelab_docker.model.container import (
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
)
from homelab_docker.model.database.postgres import PostgresDatabaseModel
from homelab_docker.model.file.config import ConfigFileModel
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.file.config import ConfigFileResource
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ComponentResource, ResourceOptions

from ..config import BackupConfig


class BarmanResource(ComponentResource):
    RESOURCE_NAME = "barman"
    SERVER_NAME_KEY = "SERVER_NAME"
    SERVER_NAME_DEFAULT_VALUE = "all"

    DURATION_KEY = "DURATION"
    DURATION_DEFAULT_VALUE = "30m"

    def __init__(
        self,
        model: ServiceModel[BackupConfig],
        *,
        opts: ResourceOptions,
        service_name: str,
        dagu_service: DaguService,
        database_source_configs: dict[str, DatabaseSourceConfig],
        container_model_global_args: ContainerModelGlobalArgs,
        containers: dict[str, docker.Container],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = model.config.barman
        self.container_model = model.containers[self.RESOURCE_NAME]
        volume_resource = container_model_global_args.docker_resource.volume

        self.files: list[ConfigFileResource] = []
        for service_name, source_config in database_source_configs.items():
            for name, sources in source_config.postgres.items():
                for version, source in sources.items():
                    full_name = PostgresDatabaseModel.get_full_name_version(
                        service_name, name, version
                    )
                    file = ConfigFileModel(
                        container_volume_path=self.config.get_config_container_volume_path(
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
                                "minimum_redundancy": str(
                                    self.config.minimum_redundancy
                                ),
                                "retention_policy": self.config.retention_policy,
                                "local_staging_path": self.config.staging_dir.to_container_path(
                                    self.container_model.volumes
                                ).as_posix(),
                            }
                        },
                    ).build_resource(
                        full_name,
                        opts=self.child_opts,
                        volume_resource=volume_resource,
                    )
                    self.files.append(file)

        self.executor = DaguDagDockerExecutorConfig.from_container_model(
            ServiceResourceBase.add_service_name_cls(service_name, self.RESOURCE_NAME),
            self.container_model,
            service_name=service_name,
            global_args=container_model_global_args,
            service_args=None,
            build_args=ContainerModelBuildArgs(files=self.files),
            containers=containers,
        )

        # Spawn a docker container for debugging purpose
        self.debug_name = "{}-debug".format(self.RESOURCE_NAME)
        self.debug = DaguDagConfig(
            path=PosixPath("{}-{}".format(service_name, self.debug_name)),
            name=self.debug_name,
            group=service_name,
            tags=[self.RESOURCE_NAME],
            params={self.DURATION_KEY: self.DURATION_DEFAULT_VALUE},
            steps=[
                DaguDagStepConfig(
                    name="hang",
                    command="1h",
                    executor=self.executor.to_hang_executor(),
                ),
            ],
        ).build_resource(
            "dagu-debug",
            opts=self.child_opts,
            dagu_service=dagu_service,
            volume_resource=volume_resource,
        )

        # Run barman check manually
        self.check_name = "{}-check".format(self.RESOURCE_NAME)
        self.check = DaguDagConfig(
            path=PosixPath("{}-{}".format(service_name, self.check_name)),
            name=self.check_name,
            group=service_name,
            tags=[self.RESOURCE_NAME],
            params={self.SERVER_NAME_KEY: self.SERVER_NAME_DEFAULT_VALUE},
            steps=[
                DaguDagStepConfig(
                    name="check",
                    command="check ${{{}}}".format(self.SERVER_NAME_KEY),
                    executor=self.executor,
                ),
            ],
        ).build_resource(
            "dagu-check",
            opts=self.child_opts,
            dagu_service=dagu_service,
            volume_resource=volume_resource,
        )

        # Run barman switch-wal manually
        self.switch_wal_name = "{}-switch-wal".format(self.RESOURCE_NAME)
        self.switch_wal = DaguDagConfig(
            path=PosixPath("{}-{}".format(service_name, self.switch_wal_name)),
            name=self.switch_wal_name,
            group=service_name,
            tags=[self.RESOURCE_NAME],
            params={self.SERVER_NAME_KEY: self.SERVER_NAME_DEFAULT_VALUE},
            steps=[
                DaguDagStepConfig(
                    name="switch-wal",
                    command="switch-wal --force --archive ${{{}}}".format(
                        self.SERVER_NAME_KEY
                    ),
                    executor=self.executor,
                ),
            ],
        ).build_resource(
            "dagu-switch-wal",
            opts=self.child_opts,
            dagu_service=dagu_service,
            volume_resource=volume_resource,
        )

        # Run barman cron every minute
        self.cron_name = "{}-cron".format(self.RESOURCE_NAME)
        self.cron = DaguDagConfig(
            path=PosixPath("{}-{}".format(service_name, self.cron_name)),
            name=self.cron_name,
            group=service_name,
            tags=[self.RESOURCE_NAME],
            schedule="* * * * *",
            max_active_runs=1,
            steps=[
                DaguDagStepConfig(
                    name="cron",
                    command="cron --keep-descriptors",
                    executor=self.executor,
                )
            ],
        ).build_resource(
            "dagu-cron",
            opts=self.child_opts,
            dagu_service=dagu_service,
            volume_resource=volume_resource,
        )

        # Run barman backup every day
        self.backup_name = "{}-backup".format(self.RESOURCE_NAME)
        self.backup = DaguDagConfig(
            path=PosixPath("{}-{}".format(service_name, self.backup_name)),
            name=self.backup_name,
            group=service_name,
            tags=[self.RESOURCE_NAME],
            schedule="0 0 * * *",
            max_active_runs=1,
            params={self.SERVER_NAME_KEY: self.SERVER_NAME_DEFAULT_VALUE},
            steps=[
                DaguDagStepConfig(
                    name="backup",
                    command="backup ${{{}}} --wait".format(self.SERVER_NAME_KEY),
                    executor=self.executor,
                ),
            ],
        ).build_resource(
            "dagu-backup",
            opts=self.child_opts,
            dagu_service=dagu_service,
            volume_resource=volume_resource,
        )

        self.register_outputs({})
