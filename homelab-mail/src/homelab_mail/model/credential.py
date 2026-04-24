from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class MailCredentialModel(HomelabBaseModel):
    host: str
    port: PositiveInt
    address: str
    username: str | None = None
    password: str
