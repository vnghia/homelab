import pulumi_tls as tls
from pulumi import ResourceOptions

from . import SecretModel


class SecretKeyModel(SecretModel):
    algorithm: str

    def build_resource(
        self, resource_name: str, opts: ResourceOptions
    ) -> tls.PrivateKey:
        opts = self.opts(opts)
        return tls.PrivateKey(resource_name, opts=opts, algorithm=self.algorithm)
