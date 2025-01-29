from homelab import network
from homelab.docker import Docker


class Homelab:
    def __init__(self) -> None:
        self.docker = Docker()
        self.dns = network.Dns(
            ips={
                "private": {
                    "v4": self.docker.service.tailscale.ipv4,
                    "v6": self.docker.service.tailscale.ipv6,
                }
            }
        )
