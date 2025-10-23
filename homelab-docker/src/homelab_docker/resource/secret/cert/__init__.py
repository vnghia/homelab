from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_pydantic import HomelabRootModel
from homelab_secret.model.cert import SecretCertModel
from homelab_secret.model.cert.locally_signed import SecretLocallySignedCertModel
from homelab_secret.resource import SecretResource
from pulumi import ResourceOptions

from .locally_signed import SecretLocallySignedCertBuilder
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
    ) -> tls.SelfSignedCert | tls.LocallySignedCert:
        root = self.root.root
        return (
            SecretLocallySignedCertBuilder(root)
            if isinstance(root, SecretLocallySignedCertModel)
            else SecretSelfSignedCertBuilder(root)
        ).build_resource(resource_name, opts, resource, extractor_args)
