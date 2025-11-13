from homelab_pydantic import HomelabRootModel

from .cert import SecretCertModel
from .key import SecretKeyModel
from .password import SecretPasswordModel
from .uuid import SecretUuidModel


class SecretModel(
    HomelabRootModel[
        SecretCertModel | SecretPasswordModel | SecretUuidModel | SecretKeyModel
    ]
):
    pass
