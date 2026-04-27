from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ..model.stalwart import MailStalwartListenerModel


class MailStalwartRecoveryConfig(HomelabBaseModel):
    enabled: bool
    address: GlobalExtract
    username: GlobalExtract
    password: GlobalExtract


class MailStalwartListenerConfig(
    HomelabRootModel[dict[str, MailStalwartListenerModel]]
):
    root: dict[str, MailStalwartListenerModel]


class MailStalwartConfig(HomelabBaseModel):
    recovery: MailStalwartRecoveryConfig
    listener: MailStalwartListenerConfig
