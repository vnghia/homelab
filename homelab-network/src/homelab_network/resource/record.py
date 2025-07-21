from collections import defaultdict

import pulumi
from pulumi import ComponentResource, ResourceOptions
from pydantic import IPvAnyAddress

from ..config.record import RecordConfig
from ..model.ip import NetworkIpModel, NetworkIpOutputModel, NetworkIpSource


class RecordResource(ComponentResource):
    RESOURCE_NAME = "record"

    def __init__(
        self,
        name: str,
        config: RecordConfig,
        *,
        opts: ResourceOptions | None,
        source_ips: dict[NetworkIpSource, NetworkIpOutputModel],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        public_ip_model = config.public_ip.root
        public_ip = None
        if isinstance(public_ip_model, NetworkIpModel):
            public_ip = NetworkIpOutputModel.from_model(public_ip_model)
        else:
            public_ip = source_ips[public_ip_model]

        self.records = {
            key: [
                record.build_resource(
                    "{}-{}-{}".format(name, key, key_ip),
                    opts=self.child_opts,
                    zone_id=config.zone_id,
                    ip=ip,
                )
                for key_ip, ip in public_ip.to_dict().items()
            ]
            for key, record in config.records.items()
        }
        self.hostnames = config.hostnames

        self.local_records: defaultdict[IPvAnyAddress, set[str]] = defaultdict(set)
        for key, hostname in self.hostnames.items():
            pulumi.export("record.{}.{}".format(name, key), hostname)
            if config.local_ip:
                self.local_records[config.local_ip.v4].add(hostname)
                self.local_records[config.local_ip.v6].add(hostname)
        self.register_outputs({})
