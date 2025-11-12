from homelab_docker.config.service.network import ServiceNetworkProxyEgressType
from homelab_pydantic import HomelabBaseModel

from ..model.entrypoint import TraefikEntrypointModel


class TraefikEntrypointConfig(HomelabBaseModel):
    config: dict[str, TraefikEntrypointModel]
    mapping: dict[str, str]
    local: str | None = None
    internal: str | None = None
    egress: dict[ServiceNetworkProxyEgressType, str] | None = None

    @property
    def local_(self) -> str:
        if not self.local:
            raise ValueError("Local entrypoint is not configured")
        return self.local

    @property
    def internal_(self) -> str:
        if not self.internal:
            raise ValueError("Internal entrypoint is not configured")
        return self.internal

    @property
    def egress_(self) -> dict[ServiceNetworkProxyEgressType, str]:
        if not self.egress:
            raise ValueError("Egress entrypoint is not configured")
        return self.egress
