import pulumi_cloudflare as cloudflare
from pulumi import Input, Output, ResourceOptions
from pydantic import BaseModel, ConfigDict, IPvAnyAddress


class Record(BaseModel):
    model_config = ConfigDict(strict=True)

    zone_id: str
    name: str

    def build_resource(
        self,
        resource_name: str,
        ip: Input[IPvAnyAddress],
        opts: ResourceOptions | None = None,
    ) -> cloudflare.Record:
        type = Output.from_input(ip).apply(lambda x: "A" if x.version == 4 else "AAAA")
        return cloudflare.Record(
            resource_name,
            opts=opts,
            zone_id=self.zone_id,
            name=self.name,
            content=Output.from_input(ip).apply(str),
            comment="record for {}".format(resource_name),
            proxied=False,
            type=type,
        )
