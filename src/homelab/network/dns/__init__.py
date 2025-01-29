from pulumi import ComponentResource, Input, ResourceOptions
from pydantic import IPvAnyAddress

from homelab import config
from homelab.network.dns.record import Record


class Dns(ComponentResource):
    RESOURCE_NAME = "dns"

    def __init__(self, ips: dict[str, dict[str, Input[IPvAnyAddress]]]) -> None:
        self.config = config.network.dns

        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.records = {
            k: Record(name=k, config=v, ips=ips[k]) for k, v in self.config.items()
        }
