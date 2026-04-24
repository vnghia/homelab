from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from .credential import MailCredentialConfig
from .noreply import NoReplyConfig


class MailAddressConfig(HomelabBaseModel):
    hostname: str
    record: str
    port: PositiveInt


class MailConfig(HomelabBaseModel):
    address: MailAddressConfig
    custom: MailCredentialConfig = MailCredentialConfig()
    noreply: NoReplyConfig = NoReplyConfig()
