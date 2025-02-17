import pulumi
import pulumi_random as random
from homelab_dagu_service import DaguService
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from .config import ResticConfig
from .resource.repo import ResticRepoResource


class ResticService(ServiceResourceBase[ResticConfig]):
    PASSWORD_LENGTH = 64

    def __init__(
        self,
        model: ServiceModel[ResticConfig],
        *,
        opts: ResourceOptions | None,
        dagu_service: DaguService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

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

        pulumi.export("restic.repo", self.repo.id)
        pulumi.export("restic.password", self.password.result)

        self.register_outputs({})
