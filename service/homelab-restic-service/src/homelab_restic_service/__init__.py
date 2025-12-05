from collections import defaultdict
from pathlib import PosixPath

from homelab_backup.config import BackupGlobalConfig
from homelab_balite_service import BaliteService
from homelab_barman_service import BarmanService
from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.database.type import DatabaseType
from homelab_docker.model.docker.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_pydantic import RelativePath
from pulumi import ResourceOptions

from .config import ResticConfig
from .config.volume import ResticVolumeConfig
from .model.profile import ResticProfileModel
from .model.profile.database import ResticProfileDatabaseModel
from .resource.profile.global_ import ResticGlobalProfileResource


class ResticService(ServiceWithConfigResourceBase[ResticConfig]):
    DEFAULT_PROFILE_NAME = "default"

    def __init__(
        self,
        model: ServiceWithConfigModel[ResticConfig],
        *,
        opts: ResourceOptions,
        backup_config: BackupGlobalConfig,
        barman_service: BarmanService,
        balite_service: BaliteService,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.backup_config = backup_config

        self.configuration_dir_volume_path = GlobalExtractor(
            self.config.configuration_dir
        ).extract_volume_path(self.extractor_args)

        self.database_configs = []
        self.volume_configs = []

        self.database_configs.append(
            self.build_database_config(
                balite_service.config.root,
                DatabaseType.SQLITE,
                RelativePath(PosixPath("")),
            )
        )

        for (
            name,
            volume_model,
        ) in self.extractor_args.host_model.docker.volumes.local.items():
            if volume_model.backup:
                self.volume_configs.append(
                    ResticVolumeConfig(name=name, model=volume_model)
                )

        self.service_groups: defaultdict[str, list[str]] = defaultdict(list)
        self.profiles = []

        for volume in sorted(self.volume_configs, key=lambda x: x.name):
            profile = ResticProfileModel(volume=volume).build_resource(
                opts=self.child_opts, restic_service=self
            )
            self.profiles.append(profile)
            self.service_groups[profile.volume.service].append(profile.volume.name)

        self.service_database_groups: defaultdict[
            str, defaultdict[DatabaseType, list[str]]
        ] = defaultdict(lambda: defaultdict(list))
        self.database_profiles = []

        for names in barman_service.service_maps.values():
            for map_name in names:
                profile = ResticProfileDatabaseModel(
                    type_=DatabaseType.POSTGRES, name=map_name.full
                ).build_resource(opts=self.child_opts, restic_service=self)
                self.database_profiles.append(profile)
                self.service_database_groups[profile.volume.service][
                    profile.type_
                ].append(profile.volume.name)

                self.database_configs.append(
                    self.build_database_config(
                        map_name.backup,
                        DatabaseType.POSTGRES,
                        RelativePath(PosixPath(map_name.full)),
                    )
                )

        for name in balite_service.service_maps:
            profile = ResticProfileDatabaseModel(
                type_=DatabaseType.SQLITE,
                name="{}-{}".format(name, DatabaseType.SQLITE.value),
            ).build_resource(opts=self.child_opts, restic_service=self)
            self.database_profiles.append(profile)
            self.service_database_groups[profile.volume.service][profile.type_].append(
                profile.volume.name
            )

        self.global_ = ResticGlobalProfileResource(
            opts=self.child_opts, restic_service=self
        )

        # No need to specify file dependencies because the file are created after `pulumi up`
        self.options[None].add_volumes(
            {
                config.name: config.container_volume_config
                for config in self.volume_configs
            }
            | {
                config.name: config.container_volume_config
                for config in self.database_configs
            }
        )

        self.register_outputs({})

    def get_global_profile_volume_path(self) -> ContainerVolumePath:
        return self.configuration_dir_volume_path / "profiles"

    def get_profile_volume_path(self, name: str) -> ContainerVolumePath:
        return self.configuration_dir_volume_path / "profiles.d" / name

    @classmethod
    def get_database_group(cls, service: str) -> str:
        return "{}-database".format(service)

    def build_database_config(
        self, name: str, type: DatabaseType, path: RelativePath
    ) -> ResticVolumeConfig:
        return ResticVolumeConfig(
            name=name,
            model=self.extractor_args.host_model.docker.volumes.local.get(
                name, ResticProfileModel.DEFAULT_VOLUME_MODEL
            ),
            relative=RelativePath(PosixPath(type)) / path,
        )
