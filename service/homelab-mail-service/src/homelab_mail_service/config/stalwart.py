from homelab_extract import GlobalExtract
from homelab_pydantic.model import HomelabBaseModel
from pydantic import PositiveInt


class MailStalwartRecoveryConfig(HomelabBaseModel):
    enabled: bool
    port: PositiveInt
    username: GlobalExtract
    password: GlobalExtract


class MailStalwartConfig(HomelabBaseModel):
    recovery: MailStalwartRecoveryConfig
