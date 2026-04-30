from homelab_pydantic import HomelabRootModel

from ..model.credential import MailCredentialModel


class MailCredentialConfig(HomelabRootModel[dict[str, MailCredentialModel]]):
    root: dict[str, MailCredentialModel] = {}

    def __getitem__(self, key: str) -> MailCredentialModel:
        return self.root[key]
