from homelab_pydantic import HomelabRootModel
from homelab_secret.model import SecretModel


class ServiceSecretConfig(HomelabRootModel[dict[str, SecretModel]]):
    pass
