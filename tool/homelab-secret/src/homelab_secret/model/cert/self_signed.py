from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_extract.plain import PlainArgs
from pulumi import ResourceOptions

from .base import SecretCertBaseModel

if typing.TYPE_CHECKING:
    from ...resource import SecretResource


class SecretSelfSignedCertModel(SecretCertBaseModel):
    key: str | None

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource,
        plain_args: PlainArgs,
        key: tls.PrivateKey | None,
    ) -> tls.SelfSignedCert:
        opts = self.opts(opts)
        key = resource.get_key(self.key, key)

        return tls.SelfSignedCert(
            resource_name,
            opts=opts,
            allowed_uses=self.allowed_uses,
            private_key_pem=key.private_key_pem,
            dns_names=[dns.extract_str(plain_args) for dns in self.dns]
            if self.dns
            else None,
            subject=self.subject.to_args(False, plain_args) if self.subject else None,
            validity_period_hours=self.validity_period_hours,
            is_ca_certificate=self.is_ca_certificate,
        )
