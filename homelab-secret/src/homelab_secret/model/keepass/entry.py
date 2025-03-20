from homelab_pydantic import HomelabBaseModel
from pydantic import HttpUrl

from .. import SecretModel
from .username import KeepassUsernameModel


class KeepassEntryModel(HomelabBaseModel):
    username: KeepassUsernameModel
    password: SecretModel | str = SecretModel()
    hostname: str
    urls: list[HttpUrl] = []
    apps: list[str] = []
