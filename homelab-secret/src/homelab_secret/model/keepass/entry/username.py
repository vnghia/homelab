from homelab_extract.plain import PlainArgs
from homelab_extract.plain.hostname import GlobalPlainExtractHostnameSource
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output, ResourceOptions

from ...password import SecretPasswordModel


class KeepassEntryUsernameEmailModel(HomelabBaseModel):
    address: SecretPasswordModel = SecretPasswordModel(length=8, special=False)
    hostname: GlobalPlainExtractHostnameSource
    force_lower: bool = False

    def to_email(self, opts: ResourceOptions, plain_args: PlainArgs) -> Output[str]:
        address = self.address.build_resource(
            "address", opts, None, plain_args
        ).result.apply(lambda address: address.lower() if self.force_lower else address)
        return Output.concat(address, "@", self.hostname.to_url(plain_args))


class KeepassEntryUsernameModel(
    HomelabRootModel[KeepassEntryUsernameEmailModel | SecretPasswordModel | str]
):
    root: KeepassEntryUsernameEmailModel | SecretPasswordModel | str = (
        SecretPasswordModel(length=16, special=False)
    )

    def to_username(self, opts: ResourceOptions, plain_args: PlainArgs) -> Output[str]:
        root = self.root
        if isinstance(root, KeepassEntryUsernameEmailModel):
            return root.to_email(opts=opts, plain_args=plain_args)
        if isinstance(root, SecretPasswordModel):
            return root.build_resource("username", opts, None, plain_args).result
        return Output.from_input(root)
