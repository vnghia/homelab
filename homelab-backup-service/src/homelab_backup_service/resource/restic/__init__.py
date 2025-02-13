from pathlib import PosixPath

import pulumi
import pulumi_docker as docker
import pulumi_random as random
from homelab_backup_service.config.backup import BackupConfig
from homelab_backup_service.resource.restic.repo import ResticRepoResource
from homelab_dagu_service import DaguService
from homelab_dagu_service.config import DaguDagConfig
from homelab_dagu_service.config.executor.docker import DaguDagDockerExecutorConfig
from homelab_dagu_service.config.step import DaguDagStepConfig
from homelab_docker.config.volume import VolumeConfig
from homelab_docker.model.container.model import ContainerModelGlobalArgs
from homelab_docker.model.container.volume import (
    ContainerVolumeConfig,
    ContainerVolumesConfig,
)
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ComponentResource, ResourceOptions


class ResticResource(ComponentResource):
    RESOURCE_NAME = "restic"
    RESTIC_MOUNT_PATH = PosixPath("/") / RESOURCE_NAME

    def __init__(
        self,
        model: ServiceModel[BackupConfig],
        *,
        opts: ResourceOptions,
        service_name: str,
        volume_config: VolumeConfig,
        dagu_service: DaguService,
        container_model_global_args: ContainerModelGlobalArgs,
        containers: dict[str, docker.Container],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = model.config.restic
        self.container_model = model.containers[self.RESOURCE_NAME]
        volume_resource = container_model_global_args.docker_resource.volume

        self.password = random.RandomPassword(
            "password",
            opts=ResourceOptions.merge(self.child_opts, ResourceOptions(protect=True)),
            length=64,
        )
        self.repo = ResticRepoResource(
            "repo",
            self.config,
            opts=self.child_opts,
            password=self.password.result,
            s3_integration_config=dagu_service.s3_integration_config,
            image_resource=container_model_global_args.docker_resource.image,
        )

        self.restic_env = dagu_service.build_env_file(
            "env",
            opts=self.child_opts,
            name="restic",
            envs={
                "RESTIC_REPOSITORY": self.repo.id,
                "RESTIC_PASSWORD": self.password.result,
            },
        )

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
                    )
                }
            ),
            service_name=service_name,
            global_args=container_model_global_args,
            service_args=None,
            build_args=None,
            containers=containers,
        )

        self.check_name = "{}-check".format(self.RESOURCE_NAME)
        self.check = DaguDagConfig(
            path=PosixPath("{}-{}".format(service_name, self.check_name)),
            name=self.check_name,
            group=service_name,
            tags=[self.RESOURCE_NAME],
            steps=[
                DaguDagStepConfig(
                    name="check", command="check --read-data", executor=self.executor
                ),
            ],
        ).build_resource(
            "dagu-check",
            opts=self.child_opts,
            dagu_service=dagu_service,
            volume_resource=volume_resource,
            env_files=[dagu_service.aws_env, self.restic_env],
        )

        pulumi.export("restic.repo", self.repo.id)
        pulumi.export("restic.password", self.password.result)

        self.register_outputs({})
