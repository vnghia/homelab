from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabRootModel
from pydantic import PositiveInt


class MailCredential(HomelabBaseModel):
    host: str
    port: PositiveInt
    address: str
    username: str | None = None
    password: str


class MailConfig(HomelabRootModel[dict[str, MailCredential]]):
    root: dict[str, MailCredential] = {}

    def __getitem__(self, key: str) -> MailCredential:
        return self.root[key]
