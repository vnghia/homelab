from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from .credential import MailCredentialConfig
from .noreply import NoReplyConfig


class MailVariableConfig(HomelabBaseModel):
    host: str
    port: str


class MailAddressConfig(HomelabBaseModel):
    hostname: str
    record: str
    port: PositiveInt
    variable: MailVariableConfig


class MailConfig(HomelabBaseModel):
    address: MailAddressConfig
    custom: MailCredentialConfig = MailCredentialConfig()
    noreply: NoReplyConfig = NoReplyConfig()
