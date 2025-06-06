from homelab_pydantic import HomelabBaseModel
from pydantic import IPvAnyAddress

from .port import NetworkPortConfig
from .record import RecordConfig


class NetworkConfig(HomelabBaseModel):
    public_ips: dict[str, IPvAnyAddress]
    public: RecordConfig
    private: RecordConfig
    port: NetworkPortConfig

    @property
    def aliases(self) -> list[str]:
        return self.public.aliases + self.private.aliases
