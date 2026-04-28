from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ..model.stalwart import MailStalwartListenerModel


class MailStalwartRecoveryConfig(HomelabBaseModel):
    enabled: bool
    admin: bool
    address: GlobalExtract
    username: GlobalExtract
    password: GlobalExtract


class MailStalwartSystemConfig(HomelabBaseModel):
    record: str
    hostname: str
    proxies: GlobalExtract


class MailStalwartListenerConfig(
    HomelabRootModel[dict[str, MailStalwartListenerModel]]
):
    root: dict[str, MailStalwartListenerModel]


class MailStalwartConfig(HomelabBaseModel):
    recovery: MailStalwartRecoveryConfig
    system: MailStalwartSystemConfig
    listener: MailStalwartListenerConfig
