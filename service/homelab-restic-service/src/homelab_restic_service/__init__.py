from pathlib import PosixPath

import pulumi
import pulumi_random as random
from homelab_backup.config import BackupConfig
from homelab_dagu_service import DaguService
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.container.volume import ContainerVolumeConfig
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_pydantic import AbsolutePath
from pulumi import ResourceOptions

from .config import ResticConfig
from .model import ResticProfileModel
from .resource.profile.global_ import ResticGlobalProfileResource
from .resource.repo import ResticRepoResource


class ResticService(ServiceWithConfigResourceBase[ResticConfig]):
    PASSWORD_LENGTH = 64

    RESTIC_MOUNT_PREFIX = AbsolutePath(PosixPath("/"))

    DEFAULT_PROFILE_NAME = "default"

    def __init__(
        self,
        model: ServiceWithConfigModel[ResticConfig],
        *,
        opts: ResourceOptions | None,
        hostname: str,
        backup_config: BackupConfig,
        dagu_service: DaguService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.backup_config = backup_config

        self.profile_dir_volume_path = self.config.profile_dir.extract_volume_path(
            self.model
        )

        self.password = random.RandomPassword(
            "password",
            opts=ResourceOptions.merge(self.child_opts, ResourceOptions(protect=True)),
            length=self.PASSWORD_LENGTH,
        ).result
        self.repo = ResticRepoResource(
            "repo",
            self.config,
            opts=self.child_opts,
            password=self.password,
            image_resource=self.docker_resource_args.image,
        )

        self.dotenvs = [
            DotenvFileResource(
                self.name(),
                opts=self.child_opts,
                volume_path=dagu_service.get_dotenv_volume_path(self.name()),
                envs=self.config.repo.to_envs(self.password),
                volume_resource=self.docker_resource_args.volume,
            )
        ]

        self.backup_volumes = {
            volume: ContainerVolumeConfig(self.get_volume_path(volume))
            for volume, model in self.docker_resource_args.config.volumes.local.items()
            if model.backup
        }

        self.profiles = [
            ResticProfileModel(volume=volume).build_resource(
                opts=self.child_opts, restic_service=self
            )
            for volume in self.backup_volumes.keys()
        ]
        self.global_ = ResticGlobalProfileResource(
            opts=self.child_opts,
            hostname=hostname,
            profiles=self.profiles,
            restic_service=self,
        )

        # No need to specify file dependencies because the file are created after `pulumi up`
        self.docker_executor_build_args = ContainerModelBuildArgs(
            volumes=self.backup_volumes
        )

        self.dagu_dags = dagu_service.build_docker_group_dags(
            self.config.dagu,
            opts=self.child_opts,
            main_service=self,
            container_model_build_args=self.docker_executor_build_args,
            dotenvs=self.dotenvs,
        )

        pulumi.export("restic.repo", self.repo.id)
        pulumi.export("restic.password", self.password)

        self.register_outputs({})

    def get_volume_path(self, volume: str) -> AbsolutePath:
        return self.RESTIC_MOUNT_PREFIX / self.name() / volume

    def get_profile_volume_path(self, name: str) -> ContainerVolumePath:
        return self.profile_dir_volume_path / name
