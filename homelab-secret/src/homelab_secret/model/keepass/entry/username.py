from homelab_network.resource.network import Hostnames
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output, ResourceOptions

from ... import SecretModel


class KeepassEntryUsernameEmailModel(HomelabBaseModel):
    address: SecretModel = SecretModel(length=8, special=False)
    hostname: str
    public: bool

    def to_email(
        self, opts: ResourceOptions | None, hostnames: Hostnames
    ) -> Output[str]:
        address = self.address.build_resource("address", opts=opts).result
        return Output.concat(address, "@", hostnames[self.public][self.hostname])


class KeepassEntryUsernameModel(
    HomelabRootModel[KeepassEntryUsernameEmailModel | SecretModel | str]
):
    root: KeepassEntryUsernameEmailModel | SecretModel | str = SecretModel(
        length=16, special=False
    )

    def to_username(
        self, opts: ResourceOptions | None, hostnames: Hostnames
    ) -> Output[str]:
        root = self.root
        if isinstance(root, KeepassEntryUsernameEmailModel):
            return root.to_email(opts=opts, hostnames=hostnames)
        elif isinstance(root, SecretModel):
            return root.build_resource("username", opts).result
        else:
            return Output.from_input(root)
