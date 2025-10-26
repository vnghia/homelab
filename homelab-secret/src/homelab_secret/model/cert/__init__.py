from homelab_pydantic import HomelabRootModel

from .locally_signed import SecretLocallySignedCertModel
from .mtls import SecretMTlsCertModel
from .self_signed import SecretSelfSignedCertModel


class SecretCertModel(
    HomelabRootModel[
        SecretLocallySignedCertModel | SecretMTlsCertModel | SecretSelfSignedCertModel
    ]
):
    pass
