from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_pydantic import HomelabRootModel
from homelab_secret.model.cert import SecretCertModel
from homelab_secret.model.cert.locally_signed import SecretLocallySignedCertModel
from homelab_secret.model.cert.mtls import SecretMTlsCertModel
from homelab_secret.resource import SecretResource
from homelab_secret.resource.cert.mtls import SecretMTlsResource
from pulumi import ResourceOptions

from .locally_signed import SecretLocallySignedCertBuilder
from .mtls import SecretMtlsCertBuilder
from .self_signed import SecretSelfSignedCertBuilder

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class SecretCertBuilder(HomelabRootModel[SecretCertModel]):
    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource,
        extractor_args: ExtractorArgs,
    ) -> tls.SelfSignedCert | SecretMTlsResource | tls.LocallySignedCert:
        root = self.root.root
        if isinstance(root, SecretLocallySignedCertModel):
            return SecretLocallySignedCertBuilder(root).build_resource(
                resource_name, opts, resource, extractor_args, None, None, None
            )
        if isinstance(root, SecretMTlsCertModel):
            return SecretMtlsCertBuilder(root).build_resource(
                resource_name, opts, resource, extractor_args
            )
        return SecretSelfSignedCertBuilder(root).build_resource(
            resource_name, opts, resource, extractor_args, None
        )
