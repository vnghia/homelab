from homelab_pydantic import HomelabBaseModel

from ..model import MailProtocol


class NoReplyModel(HomelabBaseModel):
    hostname: str | None = None
    record: str
    username: str = "noreply"
    port: MailProtocol = MailProtocol.SMTPS
