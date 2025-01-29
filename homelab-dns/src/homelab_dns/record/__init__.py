import pulumi_cloudflare as cloudflare
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict, IPvAnyAddress


class Record(BaseModel):
    model_config = ConfigDict(strict=True)

    zone_id: str
    name: str
    ip: IPvAnyAddress

    def build_resource(
        self, resource_name: str, opts: ResourceOptions | None = None
    ) -> cloudflare.Record:
        type = "A" if self.ip.version == 4 else "AAAA"
        return cloudflare.Record(
            resource_name,
            opts=opts,
            zone_id=self.zone_id,
            name=self.name,
            comment=f"record for {resource_name}",
            proxied=False,
            tags=["pulumi"],
            type=type,
            value=str(self.ip),
        )
