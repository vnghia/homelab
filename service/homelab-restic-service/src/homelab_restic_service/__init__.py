from pathlib import PosixPath

from homelab_backup.config import BackupGlobalConfig
from homelab_docker.extract import GlobalExtract
from homelab_docker.model.container.volume import ContainerVolumeConfig
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_pydantic import AbsolutePath
from pulumi import ResourceOptions

from .config import ResticConfig
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

        self.backup_volumes = {
            volume: ContainerVolumeConfig(
                GlobalExtract.from_simple(self.get_volume_path(volume).as_posix())
            )
            for volume, model in self.docker_resource_args.config.volumes.local.items()
            if model.backup
        }

        self.profiles = [
            ResticProfileModel(volume=volume).build_resource(
                opts=self.child_opts, restic_service=self
            )
            for volume in sorted(self.backup_volumes.keys())
        ]
        self.global_ = ResticGlobalProfileResource(
            opts=self.child_opts,
            hostname=hostname,
            profiles=self.profiles,
            restic_service=self,
        )

        # No need to specify file dependencies because the file are created after `pulumi up`
        self.options[None].volumes = self.backup_volumes

        self.register_outputs({})

    def get_volume_path(self, volume: str) -> AbsolutePath:
        return self.RESTIC_MOUNT_PREFIX / self.name() / volume

    def get_profile_volume_path(self, name: str) -> ContainerVolumePath:
        return self.profile_dir_volume_path / name
