from homelab_pydantic import HomelabBaseModel


class NoReplyModel(HomelabBaseModel):
    hostname: str | None = None
    record: str
    username: str = "no-reply"
