from homelab_extract import GlobalExtract

from ...model.base import SecretBaseModel


class SecretMTlsCertModel(SecretBaseModel):
    algorithm: str
    hostname: GlobalExtract
