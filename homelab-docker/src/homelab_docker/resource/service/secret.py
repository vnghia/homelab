from __future__ import annotations

import typing

import pulumi_random as random
import pulumi_tls as tls
from homelab_secret.model.cert import SecretCertModel
from homelab_secret.resource import SecretResource
from pulumi import ComponentResource, ResourceOptions

from ...config.service.secret import ServiceSecretConfig
from ..secret.cert import SecretCertBuilder

if typing.TYPE_CHECKING:
    from ...resource.service import ServiceResourceBase


class ServiceSecretResource(ComponentResource):
    RESOURCE_NAME = "secret"

    def __init__(
        self,
        config: ServiceSecretConfig,
        *,
        opts: ResourceOptions,
        main_service: ServiceResourceBase,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, main_service.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.secrets = SecretResource(secrets={})
        for name, model in config.root.items():
            if isinstance(model, SecretCertModel):
                self.secrets.secrets[name] = SecretCertBuilder(model).build_resource(
                    name,
                    opts=self.child_opts,
                    resource=self.secrets,
                    extractor_args=main_service.extractor_args,
                )
            else:
                self.secrets.secrets[name] = model.build_resource(
                    name, opts=self.child_opts, resource=self.secrets
                )

        self.register_outputs({})

    def get_secret(self, key: str) -> random.RandomPassword | random.RandomUuid:
        return self.secrets.get_secret(key)

    def get_key(self, key: str) -> tls.PrivateKey:
        return self.secrets.get_key(key)

    def get_cert(self, key: str) -> tls.LocallySignedCert | tls.SelfSignedCert:
        return self.secrets.get_cert(key)
