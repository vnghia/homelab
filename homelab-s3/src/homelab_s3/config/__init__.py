from homelab_pydantic import HomelabBaseModel

from .b2 import B2Config
from .credential import S3CredentialConfig


class S3Config(HomelabBaseModel):
    custom: S3CredentialConfig = S3CredentialConfig()
    b2: B2Config = B2Config()
