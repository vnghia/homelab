from homelab import network
from homelab.docker import Docker


class Homelab:
    def __init__(self) -> None:
        self.docker = Docker()
        self.dns = network.Dns(tailscale=self.docker.service.tailscale)
