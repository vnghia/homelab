from homelab_pydantic import HomelabBaseModel

from ..model import MailProtocol


class NotificationModel(HomelabBaseModel):
    relay: str | None = None
    hostname: str | None = None
    record: str
    username: str = "notifications"
    port: MailProtocol = MailProtocol.SMTPS
