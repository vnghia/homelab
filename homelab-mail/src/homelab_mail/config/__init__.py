from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from ..model import MailProtocol
from .credential import MailCredentialConfig
from .noreply import NoReplyConfig
from .relay import MailRelayConfig


class MailVariableConfig(HomelabBaseModel):
    host: str
    port: str


class MailAddressConfig(HomelabBaseModel):
    hostname: str
    record: str
    port: dict[MailProtocol, PositiveInt]
    variable: MailVariableConfig


class MailConfig(HomelabBaseModel):
    address: MailAddressConfig
    relay: MailRelayConfig = MailRelayConfig()
    custom: MailCredentialConfig = MailCredentialConfig()
    noreply: NoReplyConfig = NoReplyConfig()
