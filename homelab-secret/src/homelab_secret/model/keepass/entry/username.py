from homelab_extract.hostname import GlobalExtractHostnameSource
from homelab_network.model.hostname import Hostnames
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output, ResourceOptions

from ... import SecretModel


class KeepassEntryUsernameEmailModel(HomelabBaseModel):
    address: SecretModel = SecretModel(length=8, special=False)
    hostname: GlobalExtractHostnameSource

    def to_email(self, opts: ResourceOptions, hostnames: Hostnames) -> Output[str]:
        address = self.address.build_resource("address", opts=opts).result
        return Output.concat(address, "@", self.hostname.to_hostname(hostnames))


class KeepassEntryUsernameModel(
    HomelabRootModel[KeepassEntryUsernameEmailModel | SecretModel | str]
):
    root: KeepassEntryUsernameEmailModel | SecretModel | str = SecretModel(
        length=16, special=False
    )

    def to_username(self, opts: ResourceOptions, hostnames: Hostnames) -> Output[str]:
        root = self.root
        if isinstance(root, KeepassEntryUsernameEmailModel):
            return root.to_email(opts=opts, hostnames=hostnames)
        if isinstance(root, SecretModel):
            return root.build_resource("username", opts).result
        return Output.from_input(root)
