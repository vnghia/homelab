from homelab_pydantic import HomelabRootModel

from ..model.entrypoint import TraefikEntrypointModel


class TraefikEntrypointConfig(HomelabRootModel[dict[str, TraefikEntrypointModel]]):
    pass
