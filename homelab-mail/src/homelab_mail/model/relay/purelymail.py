from typing import ClassVar

import pulumi_cloudflare as cloudflare
from homelab_pydantic import HomelabBaseModel, Hostname
from pulumi import ResourceOptions


class MailRelayPurelyMailModel(HomelabBaseModel):
    SPF_RECORD: ClassVar[str] = "v=spf1 include:_spf.purelymail.com ~all"

    DKIM_NAME_TEMPLATE: ClassVar[str] = "purelymail{i}._domainkey"
    DKIM_VALUE_TEMPLATE: ClassVar[str] = "key{i}.dkimroot.purelymail.com."

    DMARC_NAME: ClassVar[str] = "_dmarc"
    DMARC_VALUE: ClassVar[str] = "dmarcroot.purelymail.com."

    purelymail: str

    def build_resource(
        self, key: str, opts: ResourceOptions, hostname: Hostname
    ) -> None:
        cloudflare.DnsRecord(
            "purelymail-ownership-{}".format(key),
            opts=opts,
            zone_id=hostname.zone,
            name=hostname.name,
            content=self.purelymail,
            ttl=1,
            type="TXT",
        )
        cloudflare.DnsRecord(
            "purelymail-spf-{}".format(key),
            opts=opts,
            zone_id=hostname.zone,
            name=hostname.name,
            content=self.SPF_RECORD,
            ttl=1,
            type="TXT",
        )
        for i in range(1, 4):
            cloudflare.DnsRecord(
                "purelymail-dkim-{}-{}".format(i, key),
                opts=opts,
                zone_id=hostname.zone,
                name=self.DKIM_NAME_TEMPLATE.format(i=i) + "." + hostname.name,
                content=self.DKIM_VALUE_TEMPLATE.format(i=i),
                ttl=1,
                type="CNAME",
            )
        cloudflare.DnsRecord(
            "purelymail-dmarc-{}".format(key),
            opts=opts,
            zone_id=hostname.zone,
            name=self.DMARC_NAME + "." + hostname.name,
            content=self.DMARC_VALUE,
            ttl=1,
            type="CNAME",
        )
