from homelab_pydantic import HomelabBaseModel

from ..model.entrypoint import TraefikEntrypointModel


class TraefikEntrypointConfig(HomelabBaseModel):
    config: dict[str, TraefikEntrypointModel]
    mapping: dict[str, str]
    local_entrypoint: str | None = None
    internal_entrypoint: str | None = None

    @property
    def local_entrypoint_(self) -> str:
        if not self.local_entrypoint:
            raise ValueError("Local entrypoint is not configured")
        return self.local_entrypoint

    @property
    def internal_entrypoint_(self) -> str:
        if not self.internal_entrypoint:
            raise ValueError("Internal entrypoint is not configured")
        return self.internal_entrypoint
