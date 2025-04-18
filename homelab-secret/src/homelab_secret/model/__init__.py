import pulumi_random as random
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions
from pydantic import PositiveInt


class SecretModel(HomelabBaseModel):
    length: PositiveInt = 64
    uuid: bool = False
    special: bool | None = None
    protect: bool = False

    def build_resource(
        self, resource_name: str, opts: ResourceOptions | None
    ) -> random.RandomPassword | random.RandomUuid:
        opts = ResourceOptions.merge(
            opts,
            ResourceOptions(protect=self.protect, additional_secret_outputs=["result"]),
        )
        if self.uuid:
            return random.RandomUuid(resource_name, opts=opts)
        return random.RandomPassword(
            resource_name, opts=opts, length=self.length, special=self.special
        )
