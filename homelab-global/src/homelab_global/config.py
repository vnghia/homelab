from homelab_extract import GlobalExtract
from homelab_mail import MailConfig
from homelab_pydantic import HomelabBaseModel
from homelab_secret.config import SecretConfig


class GlobalConfig(HomelabBaseModel):
    mail: MailConfig = MailConfig({})
    variables: dict[str, GlobalExtract] = {}
    secrets: SecretConfig = SecretConfig()
