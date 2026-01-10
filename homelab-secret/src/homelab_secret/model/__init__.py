from homelab_pydantic import HomelabRootModel

from .cert import SecretCertModel
from .id import SecretIdModel
from .key import SecretKeyModel
from .password import SecretPasswordModel
from .uuid import SecretUuidModel


class SecretModel(
    HomelabRootModel[
        SecretCertModel
        | SecretIdModel
        | SecretPasswordModel
        | SecretUuidModel
        | SecretKeyModel
    ]
):
    pass
