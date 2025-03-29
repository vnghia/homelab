from pathlib import PosixPath

from homelab_backup.config import BackupGlobalConfig
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_pydantic import AbsolutePath, RelativePath
from pulumi import ResourceOptions

from .config import ResticConfig
from .config.volume import ResticVolumeConfig
from .model import ResticProfileModel
from .resource.profile.global_ import ResticGlobalProfileResource
from .resource.repo import ResticRepoResource


class ResticService(ServiceWithConfigResourceBase[ResticConfig]):
    RESTIC_MOUNT_PREFIX = AbsolutePath(PosixPath("/"))

    DEFAULT_PROFILE_NAME = "default"

    def __init__(
        self,
        model: ServiceWithConfigModel[ResticConfig],
        *,
        opts: ResourceOptions | None,
        hostname: str,
        backup_config: BackupGlobalConfig,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.backup_config = backup_config

        self.profile_dir_volume_path = self.config.profile_dir.extract_volume_path(
            self, None
        )

        self.repo = ResticRepoResource(
            "repo",
            opts=self.child_opts,
            image=self.docker_resource_args.image.remotes[self.config.image].image_id,
            envs=self.config.dagu.dotenvs[None].to_envs(self, None),
        )

        self.database_configs = {}
        self.volume_configs = []

        for (
            name,
            volume_model,
        ) in self.docker_resource_args.config.volumes.local.items():
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
        self.global_ = ResticGlobalProfileResource(
            opts=self.child_opts,
            hostname=hostname,
            profiles=self.profiles,
            restic_service=self,
        )

        # No need to specify file dependencies because the file are created after `pulumi up`
        self.options[None].volumes = {
            config.name: config.container_volume_config
            for config in self.database_configs.values()
        } | {
            config.name: config.container_volume_config
            for config in self.volume_configs
        }

        self.register_outputs({})

    def get_profile_volume_path(self, name: str) -> ContainerVolumePath:
        return self.profile_dir_volume_path / name
