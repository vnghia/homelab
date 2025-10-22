from __future__ import annotations

import typing

import pulumi_tls as tls
from pulumi import ResourceOptions

from .base import SecretCertBaseModel

if typing.TYPE_CHECKING:
    from ...resource import SecretResource


class SecretSelfSignedCertModel(SecretCertBaseModel):
    key: str

    def build_resource(
        self, resource_name: str, opts: ResourceOptions, resource: SecretResource
    ) -> tls.SelfSignedCert:
        opts = self.opts(opts)
        return tls.SelfSignedCert(
            resource_name,
            opts=opts,
            allowed_uses=self.allowed_uses,
            private_key_pem=resource.get_key(self.key).private_key_pem,
            validity_period_hours=self.validity_period_hours,
        )
