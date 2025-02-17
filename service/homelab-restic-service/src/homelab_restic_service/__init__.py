import pulumi
import pulumi_random as random
from homelab_dagu_service import DaguService
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
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
            data=self.config.to_envs(self.password),
            volume_resource=self.docker_resource_args.volume,
        )

        pulumi.export("restic.repo", self.repo.id)
        pulumi.export("restic.password", self.password)

        self.register_outputs({})
