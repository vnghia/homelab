import pulumi_random as random
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions
from pydantic import PositiveInt


class SecretModel(HomelabBaseModel):
    length: PositiveInt = 64
    special: bool | None = None
    protect: bool = False

    def build_resource(
        self, resource_name: str, opts: ResourceOptions | None
    ) -> random.RandomPassword:
        return random.RandomPassword(
            resource_name,
            opts=ResourceOptions.merge(opts, ResourceOptions(protect=self.protect)),
            length=self.length,
            special=self.special,
        )
