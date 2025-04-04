from homelab_pydantic import HomelabBaseModel
from pydantic import IPvAnyAddress

from .record import RecordConfig


class NetworkConfig(HomelabBaseModel):
    public_ips: dict[str, IPvAnyAddress]
    public: RecordConfig
    private: RecordConfig

    def __getitem__(self, key: bool) -> RecordConfig:
        return self.public if key else self.private
