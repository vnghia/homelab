from homelab_pydantic import HomelabRootModel

from .model import SecretModel


class SecretConfig(HomelabRootModel[dict[str, SecretModel]]):
    pass
