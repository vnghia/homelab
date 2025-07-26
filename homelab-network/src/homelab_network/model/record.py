from typing import ClassVar

import pulumi_cloudflare as cloudflare
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Input, Output, ResourceOptions
from pydantic import IPvAnyAddress, PositiveInt


class RecordFullModel(HomelabBaseModel):
    name: str
    alias: bool = False


class RecordModel(HomelabRootModel[str | RecordFullModel]):
    IPV4_VERSION: ClassVar[PositiveInt] = 4

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        zone_id: str,
        ip: Input[IPvAnyAddress],
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
        root = self.root
        return root.name if isinstance(root, RecordFullModel) else root

    def hostname(self, domain: str) -> str:
        name = self.name
        return "{}{}{}".format(
            "" if name == "@" else name,
            "" if name == "@" else ".",
            domain,
        )
