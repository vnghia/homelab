from typing import Any

import pulumi_cloudflare as cloudflare
from homelab_pydantic import HomelabBaseModel

from ..model.hostname import Hostname
from ..model.ip import NetworkIpModel, NetworkIpSource
from ..model.record import RecordModel
from .ip import NetworkIpConfig


class RecordConfig(HomelabBaseModel):
    zone_id: str
    host: str
    source_ip: NetworkIpConfig
    local_ip: NetworkIpModel | None
    records: dict[str, RecordModel]

    _domain: str
    _hostnames: dict[str, Hostname]

    def model_post_init(self, context: Any, /) -> None:
        self._domain = cloudflare.get_zone(zone_id=self.zone_id).name
        self._hostnames = {
            hostname: Hostname(value=self.records[hostname].hostname(self._domain))
            for hostname in self.records
        }

    def __getitem__(self, hostname: str) -> str:
        return self.hostnames[hostname].value

    @property
    def hostnames(self) -> dict[str, Hostname]:
        return self._hostnames

    @property
    def is_ddns(self) -> bool:
        return self.source_ip.root == NetworkIpSource.DDNS
