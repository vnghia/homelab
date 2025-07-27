import json_fix as json_fix
from homelab_config import Config, DockerConfigs
from homelab_docker.resource.service import ServiceResourceBase
from homelab_network.resource.hostname import NetworkHostnameResource
from homelab_network.resource.network import NetworkResource
from homelab_secret.resource.keepass import KeepassResource

from .host.sun import SunHost
from .host.sun.config import SunServiceConfig


class Homelab:
    def __init__(self) -> None:
        self.config = Config[SunServiceConfig].build(DockerConfigs[SunServiceConfig])
        self.project_prefix = Config.get_name(None, project=True, stack=True)

        self.network = NetworkResource(
            self.config.network, opts=None, project_prefix=self.project_prefix
        )

        self.sun = SunHost(
            self.config.dockers.sun,
            opts=None,
            project_prefix=self.project_prefix,
            network_resource=self.network,
        )

        self.keepass = KeepassResource(
            {
                service.add_service_name(name): resource
                for service in ServiceResourceBase.SERVICES.values()
                if service._keepass
                for name, resource in service._keepass.keepasses.items()
            }
        )

        self.hostname = NetworkHostnameResource(
            self.config.network, opts=None, tailscale_ip=self.sun.tailscale.ip
        )
