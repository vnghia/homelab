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
        opts: ResourceOptions,
        source_ips: dict[str, dict[NetworkIpSource, NetworkIpOutputModel]],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        if not config.is_ddns:
            source_ip_model = config.source_ip.root
            source_ip = None
            if isinstance(source_ip_model, NetworkIpModel):
                source_ip = NetworkIpOutputModel.from_model(source_ip_model)
            else:
                source_ip = source_ips[config.host][source_ip_model]

            self.records = {
                key: [
                    record.build_resource(
                        "{}-{}-{}".format(name, key, key_ip),
                        opts=self.child_opts,
                        zone_id=config.zone_id,
                        ip=ip,
                    )
                    for key_ip, ip in source_ip.data.items()
                ]
                for key, record in config.records.items()
            }
        self.hostnames = config.hostnames

        self.local_records: defaultdict[IPvAnyAddress, set[str]] = defaultdict(set)
        for key, hostname in self.hostnames.items():
            value = hostname.value
            pulumi.export("record.{}.{}".format(name, key), value)
            if config.local_ip:
                for ip in config.local_ip.root.values():
                    self.local_records[ip].add(value)
        self.register_outputs({})
