import pulumi_cloudflare as cloudflare
from homelab_pydantic import HomelabBaseModel

from homelab_network.model.record import RecordModel


class RecordConfig(HomelabBaseModel):
    zone_id: str
    records: dict[str, RecordModel]

    def get_domain(self) -> str:
        return cloudflare.get_zone(zone_id=self.zone_id).name

    def __getitem__(self, hostname: str) -> str:
        return self.records[hostname].hostname(self.get_domain())
