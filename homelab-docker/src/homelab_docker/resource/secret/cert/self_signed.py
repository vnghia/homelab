from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_pydantic import HomelabRootModel
from homelab_secret.model.cert.base import SecretCertSubjectModel
from homelab_secret.model.cert.self_signed import SecretSelfSignedCertModel
from homelab_secret.resource import SecretResource
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class SecretSelfSignedCertSubjectBuilder(HomelabRootModel[SecretCertSubjectModel]):
    def to_args(self, extractor_args: ExtractorArgs) -> tls.SelfSignedCertSubjectArgs:
        from ....extract.global_ import GlobalExtractor

        root = self.root
        return tls.SelfSignedCertSubjectArgs(
            common_name=GlobalExtractor(root.common_name).extract_str(extractor_args)
            if root.common_name
            else None,
            organizational_unit=GlobalExtractor(root.organizational_unit).extract_str(
                extractor_args
            )
            if root.organizational_unit
            else None,
        )


class SecretSelfSignedCertBuilder(HomelabRootModel[SecretSelfSignedCertModel]):
    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource,
        extractor_args: ExtractorArgs,
    ) -> tls.SelfSignedCert:
        root = self.root
        opts = root.opts(opts)
        key = resource.get_key(root.key)

        return tls.SelfSignedCert(
            resource_name,
            opts=opts,
            allowed_uses=root.allowed_uses,
            private_key_pem=key.private_key_pem,
            subject=SecretSelfSignedCertSubjectBuilder(root.subject).to_args(
                extractor_args
            )
            if root.subject
            else None,
            validity_period_hours=root.validity_period_hours,
            is_ca_certificate=root.is_ca_certificate,
        )
