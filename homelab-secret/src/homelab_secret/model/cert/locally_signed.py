from .base import SecretCertBaseModel


class SecretLocallySignedCertModel(SecretCertBaseModel):
    ca_key: str
    ca_cert: str
    key: str
