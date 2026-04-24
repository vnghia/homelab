from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class MailType(StrEnum):
    CUSTOM = auto()
    NOREPLY = auto()


class MailKey(HomelabBaseModel):
    type: MailType
    name: str


class MailCredentialHostModel(HomelabBaseModel):
    host: str
    port: str


class MailCredentialEnvKey(HomelabBaseModel):
    host: str | MailCredentialHostModel
    address: str
    username: str | None = None
    password: str
