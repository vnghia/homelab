import pulumi_random as random
from pulumi import ResourceOptions

from . import SecretModel


class SecretUuidModel(SecretModel):
    uuid: None

    def build_resource(
        self, resource_name: str, opts: ResourceOptions
    ) -> random.RandomUuid:
        opts = self.opts(opts)
        return random.RandomUuid(resource_name, opts=opts)
