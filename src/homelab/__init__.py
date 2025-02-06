from homelab_config import Config
from homelab_docker.config.docker import DockerConfig
from homelab_network.resource.network import NetworkResource

from .docker import Docker
from .docker.service import ServiceConfig


class Homelab:
    def __init__(self) -> None:
        self.config = Config[ServiceConfig].build(DockerConfig[ServiceConfig])
        self.docker = Docker(self.config)
        self.network = NetworkResource(
            self.config.network,
            opts=None,
            private_ips=self.docker.service.tailscale.ips,
        )
