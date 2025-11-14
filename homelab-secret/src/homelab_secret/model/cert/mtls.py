from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_extract.plain import GlobalPlainExtractSource, PlainArgs
from pulumi import ResourceOptions

from ...model.base import SecretBaseModel
from ...model.cert.base import SecretCertSubjectModel
from ...model.cert.locally_signed import SecretLocallySignedCertModel
from ...model.cert.self_signed import SecretSelfSignedCertModel
from ...model.key import SecretKeyModel

if typing.TYPE_CHECKING:
    from ...resource import SecretResource
    from ...resource.cert.mtls import SecretMTlsResource


class SecretMTlsCertModel(SecretBaseModel):
    algorithm: str
    hostname: GlobalPlainExtractSource

    @classmethod
    def get_resource_name(cls, t: str, resource_name: str) -> str:
        return "{}-mtls-{}".format(resource_name, t)

    @classmethod
    def build_key(
        cls,
        algorithm: str,
        key_name: str,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource,
        plain_args: PlainArgs,
    ) -> tuple[str, tls.PrivateKey]:
        full_key_name = cls.get_resource_name("{}-key".format(key_name), resource_name)
        key = SecretKeyModel(algorithm=algorithm).build_resource(
            key_name, opts, resource, plain_args
        )
        resource.secrets[full_key_name] = key
        return (full_key_name, key)

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource,
        plain_args: PlainArgs,
    ) -> SecretMTlsResource:
        from ...resource.cert.mtls import SecretMTlsResource

        opts = self.child_opts("mtls", resource_name, opts)

        ca_key = SecretKeyModel(algorithm=self.algorithm).build_resource(
            "ca-key", opts, resource, plain_args
        )
        ca_cert = SecretSelfSignedCertModel(
            key=None,
            allowed_uses=["crl_signing", "cert_signing"],
            subject=SecretCertSubjectModel(
                common_name=self.hostname,
                organizational_unit=GlobalPlainExtractSource.from_simple("CA"),
            ),
            is_ca_certificate=True,
        ).build_resource("ca-cert", opts, resource, plain_args, ca_key)

        server_key = SecretKeyModel(algorithm=self.algorithm).build_resource(
            "server-key", opts, resource, plain_args
        )
        server_cert = SecretLocallySignedCertModel(
            ca_key=None,
            ca_cert=None,
            key=None,
            allowed_uses=["server_auth"],
            dns=[self.hostname],
            subject=SecretCertSubjectModel(
                common_name=self.hostname,
                organizational_unit=GlobalPlainExtractSource.from_simple("SERVER"),
            ),
        ).build_resource(
            "server-cert", opts, resource, plain_args, ca_key, ca_cert, server_key
        )

        client_key = SecretKeyModel(algorithm=self.algorithm).build_resource(
            "client-key", opts, resource, plain_args
        )
        client_cert = SecretLocallySignedCertModel(
            ca_key=None,
            ca_cert=None,
            key=None,
            allowed_uses=["client_auth"],
            subject=SecretCertSubjectModel(
                common_name=self.hostname,
                organizational_unit=GlobalPlainExtractSource.from_simple("CLIENT"),
            ),
        ).build_resource(
            "client-cert", opts, resource, plain_args, ca_key, ca_cert, client_key
        )

        return SecretMTlsResource(
            ca_cert=ca_cert,
            server_key=server_key,
            server_cert=server_cert,
            client_key=client_key,
            client_cert=client_cert,
        )
