from __future__ import annotations

import typing

import pulumi_random as random
from pulumi import ComponentResource, ResourceOptions

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
            name: random.RandomPassword(
                name, opts=self.child_opts, length=model.length, special=model.special
            )
            for name, model in config.root.items()
        }

        self.register_outputs({})

    def __getitem__(self, key: str) -> random.RandomPassword:
        return self.secrets[key]
