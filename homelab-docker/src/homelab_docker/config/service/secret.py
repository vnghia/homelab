from homelab_pydantic import HomelabRootModel
from homelab_secret.model import SecretModel
from homelab_secret.model.key import SecretKeyModel


class ServiceSecretConfig(HomelabRootModel[dict[str, SecretModel | SecretKeyModel]]):
    pass
