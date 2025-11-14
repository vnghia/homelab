from homelab_extract import GlobalExtract
from homelab_mail import MailConfig
from homelab_pydantic import HomelabBaseModel
from homelab_s3 import S3Config
from homelab_secret.config import SecretConfig


class GlobalConfig(HomelabBaseModel):
    s3: S3Config = S3Config({})
    mail: MailConfig = MailConfig({})
    variables: dict[str, GlobalExtract] = {}
    secrets: SecretConfig = SecretConfig()
