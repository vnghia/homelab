from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_extra_service import ExtraService
from pulumi import ResourceOptions

from .config import AppriseConfig


class AppriseService(ExtraService[AppriseConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[AppriseConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)
        self.build()
