import pulumi_random as random
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from ...password import SecretPasswordModel


class KeepassEntryPasswordModel(HomelabRootModel[SecretPasswordModel]):
    root: SecretPasswordModel = SecretPasswordModel()

    def to_password(self, opts: ResourceOptions) -> random.RandomPassword:
        return self.root.build_resource("password", opts)
