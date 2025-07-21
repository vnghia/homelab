from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_network.resource.network import NetworkResource
from pulumi import ResourceOptions

from .config import DdnsConfig


class DdnsService(ServiceWithConfigResourceBase[DdnsConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[DdnsConfig],
        *,
        opts: ResourceOptions | None,
        network_resource: NetworkResource,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)
