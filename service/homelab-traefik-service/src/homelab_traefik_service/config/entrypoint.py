from homelab_docker.config.docker.network import NetworkEgressType
from homelab_pydantic import HomelabBaseModel

from ..model.entrypoint import TraefikEntrypointModel


class TraefikEntrypointConfig(HomelabBaseModel):
    config: dict[str, TraefikEntrypointModel]
    egress: dict[NetworkEgressType, str] | None = None

    @property
    def egress_(self) -> dict[NetworkEgressType, str]:
        if not self.egress:
            raise ValueError("Egress entrypoint is not configured")
        return self.egress
