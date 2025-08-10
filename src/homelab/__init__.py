import json_fix as json_fix
from homelab_config import Config, DockerConfigs
from homelab_network.model.ip import NetworkIpSource
from homelab_network.resource.hostname import NetworkHostnameResource
from homelab_network.resource.network import NetworkResource
from homelab_secret.resource.keepass import KeepassResource

from .host.earth import EarthHost
from .host.earth.config import EarthServiceConfig
from .host.sun import SunHost
from .host.sun.config import SunServiceConfig


class Homelab:
    def __init__(self) -> None:
        self.config = Config[SunServiceConfig, EarthServiceConfig].build(
            DockerConfigs[SunServiceConfig, EarthServiceConfig]
        )
        self.global_args = self.config.global_args

        self.network = NetworkResource(
            self.config.network, opts=None, global_args=self.global_args
        )

        self.docker_service_model_configs = self.config.dockers.service_model

        self.sun = SunHost(
            self.config.dockers.sun.services,
            opts=None,
            global_args=self.global_args,
            network_resource=self.network,
            docker_service_model_configs=self.docker_service_model_configs,
        )
        self.earth = EarthHost(
            self.config.dockers.earth.services,
            opts=None,
            global_args=self.global_args,
            network_resource=self.network,
            docker_service_model_configs=self.docker_service_model_configs,
        )

        self.keepass = KeepassResource(
            {
                service.add_service_name(name): resource
                for service in self.sun.services.values()
                if service._keepass
                for name, resource in service._keepass.keepasses.items()
            }
        )

        self.hostname = NetworkHostnameResource(
            self.config.network,
            opts=None,
            source_ips={
                SunHost.name(): {NetworkIpSource.TAILSCALE: self.sun.tailscale.ip}
            },
        )
