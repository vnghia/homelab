from functools import cached_property

import pulumi_cloudflare as cloudflare
from pydantic import BaseModel, ConfigDict, Field


class Dns(BaseModel):
    model_config = ConfigDict(strict=True)

    zone_id: str = Field(alias="zone-id")
    records: dict[str, str]

    @cached_property
    def hostnames(self) -> dict[str, str]:
        zone = cloudflare.get_zone(zone_id=self.zone_id)
        return {
            k: "{}{}{}".format(
                "" if v == "@" else v, "" if v == "@" else ".", zone.name
            )
            for k, v in self.records.items()
        }


class DnsMap(BaseModel):
    public: Dns
    private: Dns
