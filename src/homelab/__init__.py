import json_fix as json_fix
from homelab_config import Config, HostConfig
from homelab_network.model.ip import NetworkIpSource
from homelab_network.resource.hostname import NetworkHostnameResource
from homelab_network.resource.network import NetworkResource
from homelab_secret.resource.keepass import KeepassResource
from loguru import logger

from .host.earth import EarthHost
from .host.earth.config import EarthServiceConfig
from .host.sun import SunHost
from .host.sun.config import SunServiceConfig


class Homelab:
    @logger.catch(reraise=True)
    def __init__(self) -> None:
        self.config = Config[SunServiceConfig, EarthServiceConfig].build(
            HostConfig[SunServiceConfig, EarthServiceConfig]
        )
        self.global_args = self.config.global_args

        self.network = NetworkResource(
            self.config.network, opts=None, global_args=self.global_args
        )

        self.host_config = self.config.host.service_model

        self.sun = SunHost(
            self.config.host.sun.services,
            opts=None,
            global_args=self.global_args,
            network_resource=self.network,
            config=self.host_config,
        )
        self.earth = EarthHost(
            self.config.host.earth.services,
            opts=None,
            global_args=self.global_args,
            network_resource=self.network,
            config=self.host_config,
        )

        self.keepass = KeepassResource(
            {
                service.add_service_name(name): resource
                for service in (self.sun.services | self.earth.services).values()
                if service._keepass
                for name, resource in service._keepass.keepasses.items()
            }
        )

        self.hostname = NetworkHostnameResource(
            self.config.network,
            opts=None,
            source_ips={
                SunHost.name(): {NetworkIpSource.TAILSCALE: self.sun.tailscale.ip},
                EarthHost.name(): {NetworkIpSource.TAILSCALE: self.earth.tailscale.ip},
            },
        )
