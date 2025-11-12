from homelab_pydantic import HomelabBaseModel

from ..model.entrypoint import TraefikEntrypointModel


class TraefikEntrypointConfig(HomelabBaseModel):
    config: dict[str, TraefikEntrypointModel]
    mapping: dict[str, str]
    local: str | None = None
    internal: str | None = None

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
