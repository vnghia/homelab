from collections import defaultdict
from pathlib import PosixPath

from homelab_backup.config import BackupGlobalConfig
from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.database.type import DatabaseType
from homelab_docker.model.docker.container.volume import ContainerVolumeConfig
from homelab_docker.model.docker.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
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
        opts: ResourceOptions,
        backup_config: BackupGlobalConfig,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.backup_config = backup_config

        self.config_dir_volume_path = GlobalExtractor(
            self.config.config_dir
        ).extract_volume_path(self.extractor_args)

        self.configs: list[BarmanConfigFileResource] = []
        self.service_maps: defaultdict[str, list[str]] = defaultdict(list)

        for (
            service_name,
            service_resource,
        ) in self.extractor_args.services.items():
            database_resource = service_resource._database
            if not database_resource:
                continue
            for name, sources in database_resource.source_config.get(
                DatabaseType.POSTGRES, {}
            ).items():
                for version, (source, config) in sources.items():
                    full_name = DatabaseType.POSTGRES.get_full_name_version(
                        service_name, name, version
                    )
                    self.configs.append(
                        BarmanConfigFileResource(
                            resource_name=full_name,
                            opts=self.child_opts,
                            database_source_model=source,
                            database_config_model=config,
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
