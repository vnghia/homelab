from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from ...resource import SecretResource


from .self_signed import SecretSelfSignedCertModel


class SecretCertModel(HomelabRootModel[SecretSelfSignedCertModel]):
    def build_resource(
        self, resource_name: str, opts: ResourceOptions, resource: SecretResource
    ) -> tls.SelfSignedCert:
        return self.root.build_resource(resource_name, opts, resource)
