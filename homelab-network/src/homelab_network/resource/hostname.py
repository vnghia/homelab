from collections import defaultdict

import pulumi
from pulumi import ComponentResource, ResourceOptions
from pydantic import IPvAnyAddress

from ..config import NetworkConfig
from ..model.ip import NetworkIpOutputModel, NetworkIpSource
from .record import RecordResource


class NetworkHostnameResource(ComponentResource):
    RESOURCE_NAME = "hostname"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions | None,
        tailscale_ip: NetworkIpOutputModel,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config

        source_ips = {NetworkIpSource.TAILSCALE: tailscale_ip}

        self.records = {
            key: RecordResource(
                key, record, opts=self.child_opts, source_ips=source_ips
            )
            for key, record in config.records.items()
        }

        local_records: defaultdict[IPvAnyAddress, set[str]] = defaultdict(set)
        for record in self.records.values():
            for ip, hostnames in record.local_records.items():
                local_records[ip].update(hostnames)

        pulumi.export(
            "record.local.hosts",
            "\n".join(
                [
                    "{} {}".format(ip, " ".join(sorted(hostnames)))
                    for ip, hostnames in local_records.items()
                ]
            ),
        )
        self.register_outputs({})
