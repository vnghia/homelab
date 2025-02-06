from functools import cached_property

import pulumi_cloudflare as cloudflare
from pydantic import BaseModel, Field

from homelab_network.model.record import RecordModel


class RecordConfig(BaseModel):
    zone_id: str = Field(alias="zone-id")
    records: dict[str, RecordModel]

    @cached_property
    def hostnames(self) -> dict[str, str]:
        zone = cloudflare.get_zone(zone_id=self.zone_id)
        return {key: record.hostname(zone.name) for key, record in self.records.items()}
