from .base import SecretCertBaseModel


class SecretLocallySignedCertModel(SecretCertBaseModel):
    ca_key: str | None
    ca_cert: str | None
    key: str | None
