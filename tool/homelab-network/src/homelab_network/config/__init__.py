from homelab_pydantic import HomelabBaseModel

from .record import RecordConfig


class NetworkConfig(HomelabBaseModel):
    records: dict[str, RecordConfig]
