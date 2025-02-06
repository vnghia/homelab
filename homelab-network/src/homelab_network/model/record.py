import pulumi_cloudflare as cloudflare
from pulumi import Input, Output, ResourceOptions
from pydantic import IPvAnyAddress, RootModel


class RecordModel(RootModel[str]):
    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        zone_id: str,
        ip: Input[IPvAnyAddress],
    ) -> cloudflare.Record:
        type_ = Output.from_input(ip).apply(lambda x: "A" if x.version == 4 else "AAAA")
        return cloudflare.Record(
            resource_name,
            opts=opts,
            zone_id=zone_id,
            name=self.root,
            content=Output.from_input(ip).apply(str),
            comment="record for {}".format(resource_name),
            proxied=False,
            type=type_,
        )

    def hostname(self, zone_name: str) -> str:
        return "{}{}{}".format(
            "" if self.root == "@" else self.root,
            "" if self.root == "@" else ".",
            zone_name,
        )
