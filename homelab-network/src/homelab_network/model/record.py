from typing import ClassVar

import pulumi_cloudflare as cloudflare
from homelab_pydantic import HomelabRootModel
from netaddr_pydantic import IPAddress
from pulumi import Input, Output, ResourceOptions
from pydantic import PositiveInt


class RecordModel(HomelabRootModel[str]):
    IPV4_VERSION: ClassVar[PositiveInt] = 4

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        zone_id: str,
        ip: Input[IPAddress],
    ) -> cloudflare.DnsRecord:
        type_ = Output.from_input(ip).apply(
            lambda x: "A" if x.version == self.IPV4_VERSION else "AAAA"
        )
        return cloudflare.DnsRecord(
            resource_name,
            opts=opts,
            zone_id=zone_id,
            name=self.name,
            content=Output.from_input(ip).apply(str),
            comment="record for {}".format(resource_name),
            proxied=False,
            ttl=1,
            type=type_,
        )

    @property
    def name(self) -> str:
        return self.root

    def hostname(self, domain: str) -> str:
        name = self.name
        return "{}{}{}".format(
            "" if name == "@" else name,
            "" if name == "@" else ".",
            domain,
        )
