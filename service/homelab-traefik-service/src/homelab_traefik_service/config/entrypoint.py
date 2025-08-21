from homelab_pydantic import HomelabBaseModel

from ..model.entrypoint import TraefikEntrypointModel


class TraefikEntrypointConfig(HomelabBaseModel):
    config: dict[str, TraefikEntrypointModel]
    mapping: dict[str, str]
