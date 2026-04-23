from homelab_extra_service.config import ExtraConfig

from .stalwart import MailStalwartConfig


class MailConfig(ExtraConfig):
    stalwart: MailStalwartConfig
