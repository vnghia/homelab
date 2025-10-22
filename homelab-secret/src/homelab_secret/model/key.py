from __future__ import annotations

import typing

import pulumi_tls as tls
from pulumi import ResourceOptions
from pydantic import PositiveInt

from . import SecretModel

if typing.TYPE_CHECKING:
    from ..resource import SecretResource


class SecretKeyModel(SecretModel):
    algorithm: str
    ecdsa_curve: str | None = None
    rsa_bits: PositiveInt | None = None

    def build_resource(
        self, resource_name: str, opts: ResourceOptions, resource: SecretResource | None
    ) -> tls.PrivateKey:
        opts = self.opts(opts)
        return tls.PrivateKey(
            resource_name,
            opts=opts,
            algorithm=self.algorithm,
            ecdsa_curve=self.ecdsa_curve,
            rsa_bits=self.rsa_bits,
        )
