from homelab_pydantic import HomelabRootModel
from pulumi import Output, ResourceOptions

from ... import SecretModel


class KeepassEntryPasswordModel(HomelabRootModel[SecretModel | str]):
    root: SecretModel | str = SecretModel()

    def to_password(self, opts: ResourceOptions | None) -> Output[str]:
        root = self.root
        if isinstance(root, SecretModel):
            return root.build_resource("password", opts).result
        else:
            return Output.from_input(root)
