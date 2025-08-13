from homelab_pydantic import HomelabBaseModel
from pydantic import IPvAnyAddress


class HostIpModel(HomelabBaseModel):
    internal: IPvAnyAddress | None = None
    external: IPvAnyAddress | None = None

    @property
    def internal_(self) -> IPvAnyAddress:
        if not self.internal:
            raise ValueError("Host internal ip is not configured")
        return self.internal

    @property
    def external_(self) -> IPvAnyAddress:
        if not self.external:
            raise ValueError("Host external ip is not configured")
        return self.external
