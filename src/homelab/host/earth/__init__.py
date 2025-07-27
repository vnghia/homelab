from homelab_docker.config import DockerConfig
from homelab_network.resource.network import NetworkResource
from pulumi import ResourceOptions

from .. import HostBase
from .config import EarthServiceConfig


class EarthHost(HostBase[EarthServiceConfig]):
    def __init__(
        self,
        config: DockerConfig[EarthServiceConfig],
        *,
        opts: ResourceOptions | None,
        project_prefix: str,
        network_resource: NetworkResource,
    ) -> None:
        super().__init__(
            config,
            opts=opts,
            project_prefix=project_prefix,
            network_resource=network_resource,
        )

        self.build_extra_services()

        self.register_outputs({})
