from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_extract.plain import PlainArgs
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from .locally_signed import SecretLocallySignedCertModel
from .mtls import SecretMTlsCertModel
from .self_signed import SecretSelfSignedCertModel

if typing.TYPE_CHECKING:
    from ...resource import SecretResource
    from ...resource.cert.mtls import SecretMTlsResource


class SecretCertModel(
    HomelabRootModel[
        SecretLocallySignedCertModel | SecretMTlsCertModel | SecretSelfSignedCertModel
    ]
):
    @property
    def active(self) -> bool:
        return self.root.active

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource,
        plain_args: PlainArgs,
    ) -> tls.SelfSignedCert | SecretMTlsResource | tls.LocallySignedCert:
        root = self.root
        if isinstance(root, SecretLocallySignedCertModel):
            return root.build_resource(
                resource_name, opts, resource, plain_args, None, None, None
            )
        if isinstance(root, SecretMTlsCertModel):
            return root.build_resource(resource_name, opts, resource, plain_args)
        return root.build_resource(resource_name, opts, resource, plain_args, None)
