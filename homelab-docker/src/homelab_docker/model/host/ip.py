from homelab_pydantic import HomelabBaseModel
from netaddr_pydantic import IPAddress


class HostIpModel(HomelabBaseModel):
    internal: IPAddress | None = None
    external: IPAddress | None = None

    @property
    def internal_(self) -> IPAddress:
        if not self.internal:
            raise ValueError("Host internal ip is not configured")
        return self.internal

    @property
    def external_(self) -> IPAddress:
        if not self.external:
            raise ValueError("Host external ip is not configured")
        return self.external
