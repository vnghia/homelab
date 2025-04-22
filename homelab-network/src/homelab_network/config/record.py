import pulumi_cloudflare as cloudflare
from homelab_pydantic import HomelabBaseModel

from ..model.record import RecordFullModel, RecordModel


class RecordConfig(HomelabBaseModel):
    zone_id: str
    records: dict[str, RecordModel]

    def get_domain(self) -> str:
        return cloudflare.get_zone(zone_id=self.zone_id).name

    def __getitem__(self, hostname: str) -> str:
        return self.records[hostname].hostname(self.get_domain())

    @property
    def aliases(self) -> list[str]:
        return [
            self[hostname]
            for hostname, model in self.records.items()
            if isinstance(model.root, RecordFullModel) and model.root.alias
        ]
