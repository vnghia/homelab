import pulumi_tls as tls
from pulumi import ResourceOptions
from pydantic import PositiveInt

from . import SecretModel


class SecretKeyModel(SecretModel):
    algorithm: str
    ecdsa_curve: str | None = None
    rsa_bits: PositiveInt | None = None

    def build_resource(
        self, resource_name: str, opts: ResourceOptions
    ) -> tls.PrivateKey:
        opts = self.opts(opts)
        return tls.PrivateKey(
            resource_name,
            opts=opts,
            algorithm=self.algorithm,
            ecdsa_curve=self.ecdsa_curve,
            rsa_bits=self.rsa_bits,
        )
