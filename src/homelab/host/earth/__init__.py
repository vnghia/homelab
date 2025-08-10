from homelab_docker.config import DockerServiceModelConfigs
from homelab_global import GlobalArgs
from homelab_network.resource.network import NetworkResource
from pulumi import ResourceOptions

from .. import HostBase
from .config import EarthServiceConfig


class EarthHost(HostBase[EarthServiceConfig]):
    def __init__(
        self,
        config: EarthServiceConfig,
        *,
        opts: ResourceOptions | None,
        global_args: GlobalArgs,
        network_resource: NetworkResource,
        docker_service_model_configs: DockerServiceModelConfigs,
    ) -> None:
        super().__init__(
            config,
            opts=opts,
            global_args=global_args,
            network_resource=network_resource,
            docker_service_model_configs=docker_service_model_configs,
        )

        self.build_extra_services()

        self.register_outputs({})
