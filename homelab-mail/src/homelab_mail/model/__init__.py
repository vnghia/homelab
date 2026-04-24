from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class MailType(StrEnum):
    CUSTOM = auto()
    NO_REPLY = auto()


class MailKey(HomelabBaseModel):
    type: MailType
    name: str


class MailCredentialEnvKey(HomelabBaseModel):
    host: str
    port: str
    address: str
    username: str | None = None
    password: str
