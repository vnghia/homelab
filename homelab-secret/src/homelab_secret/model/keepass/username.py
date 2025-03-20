from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output, ResourceOptions

from .. import SecretModel


class KeepassUsernameEmailModel(HomelabBaseModel):
    email: str


class KeepassUsernameModel(
    HomelabRootModel[KeepassUsernameEmailModel | SecretModel | str]
):
    root: KeepassUsernameEmailModel | SecretModel | str = SecretModel(length=16)

    def to_username(
        self, resource_name: str, opts: ResourceOptions | None
    ) -> Output[str]:
        root = self.root
        if isinstance(root, KeepassUsernameEmailModel):
            return Output.from_input(root.email)
        elif isinstance(root, SecretModel):
            return root.build_resource(resource_name, opts).result
        else:
            return Output.from_input(root)
