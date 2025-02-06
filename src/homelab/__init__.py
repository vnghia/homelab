from homelab_config import Config
from homelab_docker.config.docker import DockerConfig

from .docker import Docker
from .docker.service import ServiceConfig


class Homelab:
    def __init__(self) -> None:
        self.config = Config[ServiceConfig].build(DockerConfig[ServiceConfig])
        self.docker = Docker(self.config.docker)
        # self.dns = network.Dns(tailscale=self.docker.service.tailscale)
