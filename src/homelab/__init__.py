from homelab import network
from homelab.docker import Docker, DockerTest


class Homelab:
    def __init__(self) -> None:
        self.docker = Docker()
        self.docker_test = DockerTest()
        self.dns = network.Dns(tailscale=self.docker.service.tailscale)
