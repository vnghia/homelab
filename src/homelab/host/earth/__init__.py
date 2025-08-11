from homelab_docker.config.host import HostServiceModelConfig
from homelab_global import GlobalArgs
from homelab_network.resource.network import NetworkResource
from pulumi import ResourceOptions

from .. import HostBase
from .config import EarthServiceConfig


class EarthHost(HostBase[EarthServiceConfig]):
    def __init__(
        self,
        service: EarthServiceConfig,
        *,
        opts: ResourceOptions | None,
        global_args: GlobalArgs,
        network_resource: NetworkResource,
        config: HostServiceModelConfig,
    ) -> None:
        super().__init__(
            service,
            opts=opts,
            global_args=global_args,
            network_resource=network_resource,
            config=config,
        )

        self.build_extra_services()

        self.register_outputs({})
