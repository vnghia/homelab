from homelab_extract import GlobalExtract
from homelab_mail import MailConfig
from homelab_pydantic import HomelabBaseModel
from homelab_s3.config.credential import S3CredentialConfig
from homelab_secret.config import SecretConfig


class GlobalConfig(HomelabBaseModel):
    s3: S3CredentialConfig = S3CredentialConfig({})
    mail: MailConfig = MailConfig({})
    variables: dict[str, GlobalExtract] = {}
    secrets: SecretConfig = SecretConfig()
