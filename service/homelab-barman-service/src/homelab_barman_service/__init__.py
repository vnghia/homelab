from collections import defaultdict
from pathlib import PosixPath

from homelab_backup.config import BackupGlobalConfig
from homelab_docker.extract import GlobalExtractor
from homelab_docker.model.container.volume import ContainerVolumeConfig
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.database.type import DatabaseType
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_extract import GlobalExtract
from homelab_pydantic import AbsolutePath
from pulumi import ResourceOptions

from .config import BarmanConfig
from .resource import BarmanConfigFileResource


class BarmanService(ServiceWithConfigResourceBase[BarmanConfig]):
    PREFIX_PATH = AbsolutePath(PosixPath("/mnt/data"))

    def __init__(
        self,
        model: ServiceWithConfigModel[BarmanConfig],
        *,
        opts: ResourceOptions | None,
        backup_config: BackupGlobalConfig,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.backup_config = backup_config

        self.config_dir_volume_path = GlobalExtractor(
            self.config.config_dir
        ).extract_volume_path(self, None)

        self.configs: list[BarmanConfigFileResource] = []
        self.service_maps: defaultdict[str, list[str]] = defaultdict(list)

        for (
            service_name,
            source_config,
        ) in self.DATABASE_SOURCE_CONFIGS.items():
            for name, sources in source_config.get(DatabaseType.POSTGRES, {}).items():
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
                    self.service_maps[service_name].append(full_name)

        self.options[None].files = self.configs
        self.options[None].volumes = {
            config.name: ContainerVolumeConfig(
                GlobalExtract.from_simple((self.PREFIX_PATH / config.name).as_posix())
            )
            for config in self.configs
        }
        self.build_containers()

        self.register_outputs({})

    def get_config_volume_path(self, name: str) -> ContainerVolumePath:
        return self.config_dir_volume_path / name
