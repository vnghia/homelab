from pydantic import BaseModel, Field

from homelab_network.model.record import RecordModel


class RecordConfig(BaseModel):
    zone_id: str = Field(alias="zone-id")
    records: dict[str, RecordModel]
