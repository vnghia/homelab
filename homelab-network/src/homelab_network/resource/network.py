from collections import defaultdict
from typing import Mapping

import pulumi
from pulumi import ComponentResource, Input, ResourceOptions
from pydantic import IPvAnyAddress

from homelab_network.config import NetworkConfig

from .record import RecordResource
from .token import TokenResource


class Hostnames(dict[bool, dict[str, str]]):
    pass


class NetworkResource(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions | None,
        private_ips: Mapping[str, Input[IPvAnyAddress]],
        project_prefix: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config

        self.public = RecordResource(
            "public", config.public, opts=self.child_opts, ips=config.public_ips
        )
        self.private = RecordResource(
            "private", config.private, opts=self.child_opts, ips=private_ips
        )
        self.token = TokenResource(
            config, opts=self.child_opts, project_prefix=project_prefix
        )

        local_records: defaultdict[IPvAnyAddress, set[str]] = defaultdict(set)
        for ip, hostnames in self.public.local_records.items():
            local_records[ip].update(hostnames)
        for ip, hostnames in self.private.local_records.items():
            local_records[ip].update(hostnames)

        pulumi.export(
            "record.local.hosts",
            "\n".join(
                [
                    "{} {}".format(ip, " ".join(hostnames))
                    for ip, hostnames in local_records.items()
                ]
            ),
        )
        self.register_outputs({})

    @property
    def hostnames(self) -> Hostnames:
        return Hostnames({True: self.public.hostnames, False: self.private.hostnames})
