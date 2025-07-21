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

        source_ip_model = config.source_ip.root
        source_ip = None
        if isinstance(source_ip_model, NetworkIpModel):
            source_ip = NetworkIpOutputModel.from_model(source_ip_model)
        else:
            source_ip = source_ips[source_ip_model]

        self.records = {
            key: [
                record.build_resource(
                    "{}-{}-{}".format(name, key, key_ip),
                    opts=self.child_opts,
                    zone_id=config.zone_id,
                    ip=ip,
                )
                for key_ip, ip in source_ip.to_dict().items()
            ]
            for key, record in config.records.items()
        }
        self.hostnames = config.hostnames
        self.public = config.public

        self.local_records: defaultdict[IPvAnyAddress, set[str]] = defaultdict(set)
        for key, hostname in self.hostnames.items():
            value = hostname.value
            pulumi.export("record.{}.{}".format(name, key), value)
            if config.local_ip:
                self.local_records[config.local_ip.v4].add(value)
                self.local_records[config.local_ip.v6].add(value)
        self.register_outputs({})
