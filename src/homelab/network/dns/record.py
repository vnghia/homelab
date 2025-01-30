from typing import Mapping

import homelab_dns as dns
import pulumi
from pulumi import ComponentResource, Input, ResourceOptions
from pydantic import IPvAnyAddress

from homelab.config.network.dns import Dns


class Record(ComponentResource):
    def __init__(
        self,
        name: str,
        config: Dns,
        ips: Mapping[str, Input[IPvAnyAddress]],
        opts: ResourceOptions | None = None,
    ) -> None:
        self.name = name
        self.config = config

        super().__init__(self.name, self.name, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)

        self.records = {
            k: [
                dns.Record(zone_id=self.config.zone_id, name=v).build_resource(
                    "{}-{}-{}".format(self.name, k, kip),
                    ip=ip,
                    opts=self.child_opts,
                )
                for kip, ip in ips.items()
            ]
            for k, v in self.config.records.items()
        }
        self.hostnames = {k: v[0].hostname for k, v in self.records.items()}

        for k, hostname in self.hostnames.items():
            pulumi.export("record-{}-{}".format(self.name, k), hostname)
        self.register_outputs(self.hostnames)
