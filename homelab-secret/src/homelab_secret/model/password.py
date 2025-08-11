import pulumi_random as random
from pulumi import ResourceOptions
from pydantic import PositiveInt

from . import SecretModel


class SecretPasswordModel(SecretModel):
    length: PositiveInt = 64
    special: bool | None = None

    def build_resource(
        self, resource_name: str, opts: ResourceOptions
    ) -> random.RandomPassword:
        opts = self.opts(opts)
        return random.RandomPassword(
            resource_name, opts=opts, length=self.length, special=self.special
        )
