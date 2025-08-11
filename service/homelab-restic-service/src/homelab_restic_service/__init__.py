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
from .resource.repo import ResticRepoResource


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

        self.profile_dir_volume_path = GlobalExtractor(
            self.config.profile_dir
        ).extract_volume_path(self.extractor_args)

        self.repo = ResticRepoResource(
            "repo",
            opts=self.child_opts,
            docker_host=self.extractor_args.host_model.access.ssh,
            image=self.extractor_args.host.docker.image.remotes[
                self.config.image
            ].image_id,
            envs=self.config.dagu.dotenvs[None].to_envs(self.extractor_args),
        )

        self.database_configs = {}
        self.volume_configs = []

        for (
            name,
            volume_model,
        ) in self.extractor_args.host_model.docker.volumes.local.items():
            config = ResticVolumeConfig(name=name, model=volume_model)
            database_type = self.config.database.find(name)
            if database_type:
                self.database_configs[database_type] = config.__replace__(
                    relative=RelativePath(PosixPath(database_type.value))
                )
            elif volume_model.backup:
                self.volume_configs.append(config)

        self.profiles = [
            ResticProfileModel(volume=volume).build_resource(
                opts=self.child_opts, restic_service=self
            )
            for volume in sorted(self.volume_configs, key=lambda x: x.name)
        ]

        self.service_groups: defaultdict[str, list[str]] = defaultdict(list)
        for profile in self.profiles:
            self.service_groups[profile.volume.service].append(profile.volume.name)

        self.database_profiles = [
            ResticProfileDatabaseModel(
                type_=DatabaseType.POSTGRES, name=name
            ).build_resource(opts=self.child_opts, restic_service=self)
            for names in barman_service.service_maps.values()
            for name in names
        ] + [
            ResticProfileDatabaseModel(
                type_=DatabaseType.SQLITE,
                name="{}-{}".format(name, DatabaseType.SQLITE.value),
            ).build_resource(opts=self.child_opts, restic_service=self)
            for name in balite_service.service_maps
        ]

        self.service_database_groups: defaultdict[
            str, defaultdict[DatabaseType, list[str]]
        ] = defaultdict(lambda: defaultdict(list))
        for profile in self.database_profiles:
            self.service_database_groups[profile.volume.service][profile.type_].append(
                profile.volume.name
            )

        self.global_ = ResticGlobalProfileResource(
            opts=self.child_opts, restic_service=self
        )

        # No need to specify file dependencies because the file are created after `pulumi up`
        self.options[None].volumes = {
            config.name: config.container_volume_config
            for config in self.volume_configs
        } | {
            config.name: config.container_volume_config
            for config in self.database_configs.values()
        }

        self.register_outputs({})

    def get_profile_volume_path(self, name: str) -> ContainerVolumePath:
        return self.profile_dir_volume_path / name

    @classmethod
    def get_database_group(cls, service: str) -> str:
        return "{}-database".format(service)
