from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions
from pydantic import PositiveInt

from . import SecretModel

if typing.TYPE_CHECKING:
    from ..resource import SecretResource


class SecretCertBaseModel(SecretModel):
    allowed_uses: list[str] = ["any_extended"]
    validity_period_hours: PositiveInt = 100 * 365 * 24  # 100 years


class SecretSelfSignedCertModel(SecretCertBaseModel):
    key: str

    def build_resource(
        self, resource_name: str, opts: ResourceOptions, resource: SecretResource
    ) -> tls.SelfSignedCert:
        opts = self.opts(opts)
        return tls.SelfSignedCert(
            resource_name,
            opts=opts,
            allowed_uses=self.allowed_uses,
            private_key_pem=resource.get_key(self.key).private_key_pem,
            validity_period_hours=self.validity_period_hours,
        )


class SecretCertModel(HomelabRootModel[SecretSelfSignedCertModel]):
    def build_resource(
        self, resource_name: str, opts: ResourceOptions, resource: SecretResource
    ) -> tls.SelfSignedCert:
        return self.root.build_resource(resource_name, opts, resource)
