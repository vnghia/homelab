from pathlib import PosixPath

import pulumi
import pulumi_random as random
from homelab_dagu_service import DaguService
from homelab_dagu_service.model import DaguDagModel
from homelab_dagu_service.model.params import DaguDagParamsModel
from homelab_dagu_service.model.step import DaguDagStepModel
from homelab_dagu_service.model.step.command import DaguDagStepCommandModel
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
from pulumi import ResourceOptions

from .config import ResticConfig
from .resource.repo import ResticRepoResource


class ResticService(ServiceResourceBase[ResticConfig]):
    PASSWORD_LENGTH = 64

    PROFILE_NAME_KEY = "PROFILE"
    RESTIC_MOUNT_PATH = PosixPath("/")

    def __init__(
        self,
        model: ServiceModel[ResticConfig],
        *,
        opts: ResourceOptions | None,
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
            envs=self.config.to_envs(self.password),
            volume_resource=self.docker_resource_args.volume,
        )

        self.backup_volumes = {
            name: ContainerVolumeConfig(self.RESTIC_MOUNT_PATH / self.name() / name)
            for name, model in volume_config.local.items()
            if model.backup
        }

        self.executor = DaguDagStepExecutorModel(
            DaguDagStepDockerExecutorModel(
                DaguDagStepDockerRunExecutorModel(model=None)
            )
        )
        self.restic_executor = DaguDagStepExecutorModel(
            DaguDagStepDockerExecutorModel(
                DaguDagStepDockerRunExecutorModel(
                    model=None, entrypoint=["/usr/bin/restic"]
                )
            )
        )

        name = "check"
        self.check = DaguDagModel(
            name=name,
            path="{}-{}".format(self.name(), name),
            group=self.name(),
            max_active_runs=1,
            params=DaguDagParamsModel({self.PROFILE_NAME_KEY: "all"}),
            steps=[
                DaguDagStepModel(
                    name=name,
                    command=[DaguDagStepCommandModel("check")],
                    executor=self.restic_executor,
                )
            ],
        ).build_resource(
            name,
            opts=self.child_opts,
            main_service=self,
            dagu_service=dagu_service,
            build_args=ContainerModelBuildArgs(volumes=self.backup_volumes),
            dotenv=self.dotenv,
        )

        pulumi.export("restic.repo", self.repo.id)
        pulumi.export("restic.password", self.password)

        self.register_outputs({})
