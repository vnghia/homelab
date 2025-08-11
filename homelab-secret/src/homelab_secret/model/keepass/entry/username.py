from homelab_extract.hostname import GlobalExtractHostnameSource
from homelab_network.model.hostname import Hostnames
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output, ResourceOptions

from ...password import SecretPasswordModel


class KeepassEntryUsernameEmailModel(HomelabBaseModel):
    address: SecretPasswordModel = SecretPasswordModel(length=8, special=False)
    hostname: GlobalExtractHostnameSource

    def to_email(self, opts: ResourceOptions, hostnames: Hostnames) -> Output[str]:
        address = self.address.build_resource("address", opts=opts).result
        return Output.concat(address, "@", self.hostname.to_hostname(hostnames))


class KeepassEntryUsernameModel(
    HomelabRootModel[KeepassEntryUsernameEmailModel | SecretPasswordModel | str]
):
    root: KeepassEntryUsernameEmailModel | SecretPasswordModel | str = (
        SecretPasswordModel(length=16, special=False)
    )

    def to_username(self, opts: ResourceOptions, hostnames: Hostnames) -> Output[str]:
        root = self.root
        if isinstance(root, KeepassEntryUsernameEmailModel):
            return root.to_email(opts=opts, hostnames=hostnames)
        if isinstance(root, SecretPasswordModel):
            return root.build_resource("username", opts).result
        return Output.from_input(root)
