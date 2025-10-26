from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabRootModel
from homelab_secret.model.cert.base import SecretCertSubjectModel
from homelab_secret.model.cert.locally_signed import SecretLocallySignedCertModel
from homelab_secret.model.cert.mtls import SecretMTlsCertModel
from homelab_secret.model.cert.self_signed import SecretSelfSignedCertModel
from homelab_secret.model.key import SecretKeyModel
from homelab_secret.resource import SecretResource
from homelab_secret.resource.cert.mtls import SecretMTlsResource
from pulumi import ResourceOptions

from homelab_docker.resource.secret.cert.locally_signed import (
    SecretLocallySignedCertBuilder,
)

from .self_signed import SecretSelfSignedCertBuilder

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class SecretMtlsCertBuilder(HomelabRootModel[SecretMTlsCertModel]):
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
    ) -> tuple[str, tls.PrivateKey]:
        full_key_name = cls.get_resource_name("{}-key".format(key_name), resource_name)
        key = SecretKeyModel(algorithm=algorithm).build_resource(
            key_name, opts, resource
        )
        resource.secrets[full_key_name] = key
        return (full_key_name, key)

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource,
        extractor_args: ExtractorArgs,
    ) -> SecretMTlsResource:
        root = self.root
        opts = root.child_opts("mtls", resource_name, opts)

        ca_key = SecretKeyModel(algorithm=root.algorithm).build_resource(
            "ca-key", opts, resource
        )
        ca_cert = SecretSelfSignedCertBuilder(
            SecretSelfSignedCertModel(
                key=None,
                allowed_uses=["crl_signing", "cert_signing"],
                subject=SecretCertSubjectModel(
                    common_name=root.hostname,
                    organizational_unit=GlobalExtract.from_simple("CA"),
                ),
                is_ca_certificate=True,
            )
        ).build_resource("ca-cert", opts, resource, extractor_args, ca_key)

        server_key = SecretKeyModel(algorithm=root.algorithm).build_resource(
            "server-key", opts, resource
        )
        server_cert = SecretLocallySignedCertBuilder(
            SecretLocallySignedCertModel(
                ca_key=None,
                ca_cert=None,
                key=None,
                allowed_uses=["server_auth"],
                dns=[root.hostname],
                subject=SecretCertSubjectModel(
                    common_name=root.hostname,
                    organizational_unit=GlobalExtract.from_simple("SERVER"),
                ),
            )
        ).build_resource(
            "server-cert", opts, resource, extractor_args, ca_key, ca_cert, server_key
        )

        client_key = SecretKeyModel(algorithm=root.algorithm).build_resource(
            "client-key", opts, resource
        )
        client_cert = SecretLocallySignedCertBuilder(
            SecretLocallySignedCertModel(
                ca_key=None,
                ca_cert=None,
                key=None,
                allowed_uses=["client_auth"],
                subject=SecretCertSubjectModel(
                    common_name=root.hostname,
                    organizational_unit=GlobalExtract.from_simple("CLIENT"),
                ),
            )
        ).build_resource(
            "client-cert", opts, resource, extractor_args, ca_key, ca_cert, client_key
        )

        return SecretMTlsResource(
            ca_cert=ca_cert,
            server_key=server_key,
            server_cert=server_cert,
            client_key=client_key,
            client_cert=client_cert,
        )
