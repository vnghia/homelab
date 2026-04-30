from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_extract.plain import PlainArgs
from pulumi import ResourceOptions

from .base import SecretCertBaseModel

if typing.TYPE_CHECKING:
    from ...resource import SecretResource


class SecretLocallySignedCertModel(SecretCertBaseModel):
    ca_key: str | None
    ca_cert: str | None
    key: str | None

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource,
        plain_args: PlainArgs,
        ca_key: tls.PrivateKey | None,
        ca_cert: tls.SelfSignedCert | None,
        key: tls.PrivateKey | None,
    ) -> tls.LocallySignedCert:
        opts = self.child_opts("locally-signed-cert", resource_name, opts)

        ca_key = resource.get_key(self.ca_key, ca_key)
        ca_cert = resource.get_self_signed_cert(self.ca_cert, ca_cert)

        return tls.LocallySignedCert(
            resource_name,
            opts=opts,
            allowed_uses=self.allowed_uses,
            ca_cert_pem=ca_cert.cert_pem,
            ca_private_key_pem=ca_key.private_key_pem,
            cert_request_pem=tls.CertRequest(
                resource_name,
                opts=opts,
                private_key_pem=resource.get_key(self.key, key).private_key_pem,
                dns_names=[dns.extract_str(plain_args) for dns in self.dns]
                if self.dns
                else None,
                subject=self.subject.to_args(True, plain_args)
                if self.subject
                else None,
            ).cert_request_pem,
            validity_period_hours=self.validity_period_hours,
            is_ca_certificate=self.is_ca_certificate,
        )
