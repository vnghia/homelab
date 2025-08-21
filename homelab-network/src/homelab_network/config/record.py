import pulumi_cloudflare as cloudflare
from homelab_pydantic import HomelabBaseModel

from ..model.hostname import Hostname
from ..model.ip import NetworkIpModel, NetworkIpSource
from ..model.record import RecordFullModel, RecordModel
from .ip import NetworkIpConfig


class RecordConfig(HomelabBaseModel):
    zone_id: str
    host: str
    public: bool
    source_ip: NetworkIpConfig
    local_ip: NetworkIpModel | None
    records: dict[str, RecordModel]

    def get_domain(self) -> str:
        return cloudflare.get_zone(zone_id=self.zone_id).name

    def __getitem__(self, hostname: str) -> str:
        return self.records[hostname].hostname(self.get_domain())

    @property
    def hostnames(self) -> dict[str, Hostname]:
        return {hostname: Hostname(value=self[hostname]) for hostname in self.records}

    @property
    def aliases(self) -> list[str]:
        return [
            self[hostname]
            for hostname, model in self.records.items()
            if isinstance(model.root, RecordFullModel) and model.root.alias
        ]

    @property
    def is_ddns(self) -> bool:
        return self.source_ip.root == NetworkIpSource.DDNS
