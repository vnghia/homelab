from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output, ResourceOptions

from .. import SecretModel


class KeepassEntryUsernameEmailModel(HomelabBaseModel):
    email: str


class KeepassEntryUsernameModel(
    HomelabRootModel[KeepassEntryUsernameEmailModel | SecretModel | str]
):
    root: KeepassEntryUsernameEmailModel | SecretModel | str = SecretModel(length=16)

    def to_username(self, opts: ResourceOptions | None) -> Output[str]:
        root = self.root
        if isinstance(root, KeepassEntryUsernameEmailModel):
            return Output.from_input(root.email)
        elif isinstance(root, SecretModel):
            return root.build_resource("username", opts).result
        else:
            return Output.from_input(root)
