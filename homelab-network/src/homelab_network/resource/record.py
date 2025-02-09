from typing import Mapping

import pulumi
from pulumi import ComponentResource, Input, ResourceOptions
from pydantic import IPvAnyAddress

from homelab_network.config.record import RecordConfig


class RecordResource(ComponentResource):
    RESOURCE_NAME = "record"

    def __init__(
        self,
        name: str,
        config: RecordConfig,
        *,
        opts: ResourceOptions | None,
        ips: Mapping[str, Input[IPvAnyAddress]],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.records = {
            key: [
                record.build_resource(
                    "{}-{}-{}".format(name, key, key_ip),
                    opts=self.child_opts,
                    zone_id=config.zone_id,
                    ip=ip,
                )
                for key_ip, ip in ips.items()
            ]
            for key, record in config.records.items()
        }
        self.hostnames = {k: v[0].hostname for k, v in self.records.items()}

        for key, hostname in self.hostnames.items():
            pulumi.export("record.{}.{}".format(name, key), hostname)
        self.register_outputs({})
