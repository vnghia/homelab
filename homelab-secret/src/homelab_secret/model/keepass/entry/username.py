from homelab_extract.plain import PlainArgs
from homelab_extract.plain.hostname import GlobalPlainExtractHostnameSource
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output, ResourceOptions
from pydantic import PositiveInt

from ....resource import SecretResource
from ...password import SecretPasswordModel


class KeepassEntryUsernameUsernameModel(SecretPasswordModel):
    length: PositiveInt = 16
    special: bool | None = False
    force_lower: bool = False

    def build_username(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource | None,
        plain_args: PlainArgs,
    ) -> Output[str]:
        result = (
            super().build_resource(resource_name, opts, resource, plain_args).result
        )
        return result.apply(str.lower) if self.force_lower else result


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
    HomelabRootModel[
        KeepassEntryUsernameEmailModel | KeepassEntryUsernameUsernameModel | str
    ]
):
    root: KeepassEntryUsernameEmailModel | KeepassEntryUsernameUsernameModel | str = (
        KeepassEntryUsernameUsernameModel()
    )

    def to_username(self, opts: ResourceOptions, plain_args: PlainArgs) -> Output[str]:
        root = self.root
        if isinstance(root, KeepassEntryUsernameEmailModel):
            return root.to_email(opts=opts, plain_args=plain_args)
        if isinstance(root, KeepassEntryUsernameUsernameModel):
            return root.build_username("username", opts, None, plain_args)
        return Output.from_input(root)
