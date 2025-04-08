from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import AppriseConfig


class AppriseService(ServiceWithConfigResourceBase[AppriseConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[AppriseConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.build_containers()

        self.register_outputs({})
