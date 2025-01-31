import homelab_config as config
from pulumi import ComponentResource, ResourceOptions

from homelab.docker.service.tailscale import Tailscale
from homelab.network.dns.record import Record


class Dns(ComponentResource):
    RESOURCE_NAME = "dns"

    def __init__(
        self,
        tailscale: Tailscale,
    ) -> None:
        self.config = config.network.dns

        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.public = Record(
            name="public",
            config=self.config.public,
            ips=config.network.public_ips,
            opts=self.child_opts,
        )
        self.private = Record(
            name="private",
            config=self.config.private,
            ips=tailscale.private_ips,
            opts=self.child_opts,
        )

        self.register_outputs({})
