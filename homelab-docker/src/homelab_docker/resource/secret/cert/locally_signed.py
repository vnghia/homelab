from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_pydantic import HomelabRootModel
from homelab_secret.model.cert.base import SecretCertSubjectModel
from homelab_secret.model.cert.locally_signed import SecretLocallySignedCertModel
from homelab_secret.resource import SecretResource
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class SecretLocallySignedCertSubjectBuilder(HomelabRootModel[SecretCertSubjectModel]):
    def to_args(self, extractor_args: ExtractorArgs) -> tls.CertRequestSubjectArgs:
        from ....extract.global_ import GlobalExtractor

        root = self.root
        return tls.CertRequestSubjectArgs(
            common_name=GlobalExtractor(root.common_name).extract_str(extractor_args)
            if root.common_name
            else None,
            organizational_unit=GlobalExtractor(root.organizational_unit).extract_str(
                extractor_args
            )
            if root.organizational_unit
            else None,
        )


class SecretLocallySignedCertBuilder(HomelabRootModel[SecretLocallySignedCertModel]):
    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource,
        extractor_args: ExtractorArgs,
    ) -> tls.LocallySignedCert:
        root = self.root
        opts = root.opts(opts)
        ca_key = resource.get_key(root.ca_key)
        ca_cert = resource.get_self_signed_cert(root.ca_cert)

        return tls.LocallySignedCert(
            resource_name,
            opts=opts,
            allowed_uses=root.allowed_uses,
            ca_cert_pem=ca_cert.cert_pem,
            ca_private_key_pem=ca_key.private_key_pem,
            cert_request_pem=tls.CertRequest(
                "cert-request-{}".format(resource_name),
                opts=opts,
                private_key_pem=resource.get_key(root.key).private_key_pem,
                subject=SecretLocallySignedCertSubjectBuilder(root.subject).to_args(
                    extractor_args
                )
                if root.subject
                else None,
            ).cert_request_pem,
            validity_period_hours=root.validity_period_hours,
            is_ca_certificate=root.is_ca_certificate,
        )
