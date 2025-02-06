from homelab_config import Config
from homelab_docker.config.docker import Docker as DockerConfig

from .docker import Docker
from .docker.service import Config as ServiceConfig


class Homelab:
    def __init__(self) -> None:
        self.config = Config[ServiceConfig].build(DockerConfig[ServiceConfig])
        self.docker = Docker(self.config.docker)
        # self.dns = network.Dns(tailscale=self.docker.service.tailscale)
