from __future__ import annotations

import typing

import pulumi_random as random
import pulumi_tls as tls
from pulumi import ComponentResource, Output, ResourceOptions

from ...config.service.secret import ServiceSecretConfig

if typing.TYPE_CHECKING:
    from ...resource.service import ServiceResourceBase


class ServiceSecretResouse(ComponentResource):
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

        self.secrets = {
            name: model.build_resource(name, opts=self.child_opts)
            for name, model in config.root.items()
        }

        self.register_outputs({})

    def get(
        self, key: str
    ) -> random.RandomPassword | random.RandomUuid | tls.PrivateKey:
        return self.secrets[key]

    def __getitem__(self, key: str) -> Output[str]:
        secret = self.get(key)
        if isinstance(secret, tls.PrivateKey):
            return secret.private_key_pem
        return secret.result
