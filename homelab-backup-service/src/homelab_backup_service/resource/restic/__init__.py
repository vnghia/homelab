import pulumi
import pulumi_docker as docker
import pulumi_random as random
from homelab_backup_service.config.backup import BackupConfig
from homelab_backup_service.resource.restic.repo import ResticRepoResource
from homelab_dagu_service import DaguService
from homelab_docker.model.container.model import ContainerModelGlobalArgs
from homelab_docker.model.service import ServiceModel
from homelab_integration.config.s3 import S3IntegrationConfig
from pulumi import ComponentResource, ResourceOptions


class ResticResource(ComponentResource):
    RESOURCE_NAME = "restic"

    def __init__(
        self,
        model: ServiceModel[BackupConfig],
        *,
        opts: ResourceOptions,
        service_name: str,
        s3_integration_config: S3IntegrationConfig,
        dagu_service: DaguService,
        container_model_global_args: ContainerModelGlobalArgs,
        containers: dict[str, docker.Container],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = model.config.restic
        self.container_model = model.containers[self.RESOURCE_NAME]

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
            s3_integration_config=s3_integration_config,
            image_resource=container_model_global_args.docker_resource.image,
        )

        pulumi.export("restic.repo", self.repo.id)
        pulumi.export("restic.password", self.password.result)

        self.register_outputs({})
