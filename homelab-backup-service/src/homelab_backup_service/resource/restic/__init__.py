from pathlib import PosixPath

import pulumi
import pulumi_docker as docker
import pulumi_random as random
from homelab_backup_service.resource.restic.repo import ResticRepoResource
from homelab_dagu_service import DaguService
from homelab_dagu_service.config import DaguDagConfig
from homelab_dagu_service.config.executor.docker import DaguDagDockerExecutorConfig
from homelab_dagu_service.config.step import DaguDagStepConfig
from homelab_docker.config.volume import VolumeConfig
from homelab_docker.model.container.volume import (
    ContainerVolumeConfig,
    ContainerVolumesConfig,
)
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceArgs, ServiceResourceBase
from pulumi import ComponentResource, ResourceOptions

from ...config import BackupConfig


class ResticResource(ComponentResource):
    RESOURCE_NAME = "restic"
    RESTIC_MOUNT_PATH = PosixPath("/") / RESOURCE_NAME

    PASSWORD_LENGTH = 64

    def __init__(
        self,
        model: ServiceModel[BackupConfig],
        *,
        opts: ResourceOptions,
        service_name: str,
        volume_config: VolumeConfig,
        dagu_service: DaguService,
        docker_resource_args: DockerResourceArgs,
        service_resource_args: ServiceResourceArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = model.config.restic
        self.container_model = model.containers[self.RESOURCE_NAME]
        volume_resource = docker_resource_args.volume

        self.password = random.RandomPassword(
            "password",
            opts=ResourceOptions.merge(self.child_opts, ResourceOptions(protect=True)),
            length=self.PASSWORD_LENGTH,
        )
        self.repo = ResticRepoResource(
            "repo",
            self.config,
            opts=self.child_opts,
            password=self.password.result,
            image_resource=docker_resource_args.image,
        )

        # self.restic_env = dagu_service.build_env_file(
        #     "env",
        #     opts=self.child_opts,
        #     name="restic",
        #     envs=self.config.to_envs(self.password.result),
        # )

        self.executor = DaguDagDockerExecutorConfig.from_container_model(
            ServiceResourceBase.add_service_name_cls(service_name, self.RESOURCE_NAME),
            self.container_model.model_copy(
                update={
                    "volumes": ContainerVolumesConfig.model_validate(
                        self.container_model.volumes.model_dump(by_alias=True)
                        | {
                            name: ContainerVolumeConfig(self.RESTIC_MOUNT_PATH / name)
                            for name, model in volume_config.local.items()
                            if model.backup
                        }
                    ),
                }
            ),
            service_name=service_name,
            build_args=None,
            docker_resource_args=docker_resource_args,
            service_resource_args=service_resource_args,
        )

        # self.check_name = "{}-check".format(self.RESOURCE_NAME)
        # self.check = DaguDagConfig(
        #     path=PosixPath("{}-{}".format(service_name, self.check_name)),
        #     name=self.check_name,
        #     group=service_name,
        #     tags=[self.RESOURCE_NAME],
        #     steps=[
        #         DaguDagStepConfig(
        #             name="check", command="check --read-data", executor=self.executor
        #         ),
        #     ],
        # ).build_resource(
        #     "dagu-check",
        #     opts=self.child_opts,
        #     dagu_service=dagu_service,
        #     volume_resource=volume_resource,
        #     env_files=[self.restic_env],
        # )

        pulumi.export("restic.repo", self.repo.id)
        pulumi.export("restic.password", self.password.result)

        self.register_outputs({})
