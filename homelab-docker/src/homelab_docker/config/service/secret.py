from homelab_pydantic import HomelabRootModel
from homelab_secret.model.key import SecretKeyModel
from homelab_secret.model.password import SecretPasswordModel
from homelab_secret.model.uuid import SecretUuidModel


class ServiceSecretConfig(
    HomelabRootModel[dict[str, SecretPasswordModel | SecretUuidModel | SecretKeyModel]]
):
    pass
