from homelab_backup.config import BackupConfig
from homelab_dagu_service import DaguService
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.database.type import DatabaseType
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import BarmanConfig
from .resource import BarmanConfigFileResource


class BarmanService(ServiceWithConfigResourceBase[BarmanConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[BarmanConfig],
        *,
        opts: ResourceOptions | None,
        backup_config: BackupConfig,
        dagu_service: DaguService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.backup_config = backup_config

        self.config_dir_volume_path = self.config.config_dir.extract_volume_path(
            self.model
        )

        self.configs: list[BarmanConfigFileResource] = []
        for (
            service_name,
            source_config,
        ) in self.DATABASE_SOURCE_CONFIGS.items():
            for name, sources in source_config[DatabaseType.POSTGRES].items():
                for version, source in sources.items():
                    full_name = DatabaseType.POSTGRES.get_full_name_version(
                        service_name, name, version
                    )
                    self.configs.append(
                        BarmanConfigFileResource(
                            resource_name=full_name,
                            opts=self.child_opts,
                            database_source_model=source,
                            barman_service=self,
                        )
                    )

        self.build_containers(
            options={None: ContainerModelBuildArgs(files=self.configs)}
        )

        self.dagu_dags = dagu_service.build_docker_group_dags(
            self.config.dagu,
            opts=self.child_opts,
            main_service=self,
            container_model_build_args=None,
            dotenvs=None,
        )

        self.register_outputs({})

    def get_config_volume_path(self, name: str) -> ContainerVolumePath:
        return self.config_dir_volume_path / name
