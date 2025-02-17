from homelab_pydantic import HomelabBaseModel

from homelab_network.model.record import RecordModel


class RecordConfig(HomelabBaseModel):
    zone_id: str
    records: dict[str, RecordModel]
