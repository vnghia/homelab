from homelab_extract import GlobalExtract

from ...model import SecretModel


class SecretMTlsCertModel(SecretModel):
    algorithm: str
    hostname: GlobalExtract
