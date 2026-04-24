from homelab_pydantic import HomelabBaseModel

from .credential import MailCredentialConfig


class MailConfig(HomelabBaseModel):
    custom: MailCredentialConfig = MailCredentialConfig()
