from pathlib import PosixPath

import pulumi
import pulumi_random as random
from homelab_dagu_service import DaguService
from homelab_dagu_service.model.step.executor import DaguDagStepExecutorModel
from homelab_dagu_service.model.step.executor.docker import (
    DaguDagStepDockerExecutorModel,
)
from homelab_dagu_service.model.step.executor.docker.run import (
    DaguDagStepDockerRunExecutorModel,
)
from homelab_docker.config.volume import VolumeConfig
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.container.volume import ContainerVolumeConfig
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import AbsolutePath
from pulumi import ResourceOptions

from .config import ResticConfig
from .model import ResticProfileModel
from .resource.profile.global_ import ResticGlobalProfileResource
from .resource.repo import ResticRepoResource


class ResticService(ServiceResourceBase[ResticConfig]):
    PASSWORD_LENGTH = 64

    RESTIC_MOUNT_PREFIX = AbsolutePath(PosixPath("/"))
    RESTIC_CACHE_ENV = "RESTIC_CACHE_DIR"

    BASE_PROFILE_NAME = "base"
    PROFILE_NAME_KEY = "PROFILE"

    def __init__(
        self,
        model: ServiceModel[ResticConfig],
        *,
        opts: ResourceOptions | None,
        hostname: str,
        volume_config: VolumeConfig,
        dagu_service: DaguService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

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

        self.dotenv = DotenvFileResource(
            self.name(),
            opts=self.child_opts,
            container_volume_path=dagu_service.get_dotenv_container_volume_path(
                self.name()
            ),
            envs=self.config.repo.to_envs(self.password),
            volume_resource=self.docker_resource_args.volume,
        )

        self.backup_volumes = {
            volume: ContainerVolumeConfig(self.get_volume_path(volume))
            for volume, model in volume_config.local.items()
            if model.backup
        }

        self.docker_run_executor = DaguDagStepDockerRunExecutorModel(model=None)

        self.executor = DaguDagStepExecutorModel(
            DaguDagStepDockerExecutorModel(self.docker_run_executor)
        )

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

        self.docker_executor_build_args = ContainerModelBuildArgs(
            volumes=self.backup_volumes,
            files=[profile for profile in self.profiles] + [self.global_],
        )
        self.dagu_dags = {
            dagu_service.DEBUG_DAG_NAME: dagu_service.build_debug_dag(
                self.docker_run_executor,
                opts=self.child_opts,
                main_service=self,
                container_model_build_args=self.docker_executor_build_args,
                dotenv=self.dotenv,
            )
        }

        pulumi.export("restic.repo", self.repo.id)
        pulumi.export("restic.password", self.password)

        self.register_outputs({})

    def get_volume_path(self, volume: str) -> AbsolutePath:
        return self.RESTIC_MOUNT_PREFIX / self.name() / volume
