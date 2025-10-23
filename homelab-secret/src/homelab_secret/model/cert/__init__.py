from homelab_pydantic import HomelabRootModel

from .locally_signed import SecretLocallySignedCertModel
from .self_signed import SecretSelfSignedCertModel


class SecretCertModel(
    HomelabRootModel[SecretLocallySignedCertModel | SecretSelfSignedCertModel]
):
    pass
