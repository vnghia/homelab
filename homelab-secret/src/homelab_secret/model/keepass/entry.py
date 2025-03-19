from homelab_pydantic import HomelabBaseModel
from pydantic import HttpUrl

from .. import SecretModel


class KeepassEntryModel(HomelabBaseModel):
    username: SecretModel | str = SecretModel(length=16)
    email: str | None = None
    password: SecretModel | str = SecretModel()
    hostname: str
    urls: list[HttpUrl] = []
    apps: list[str] = []
