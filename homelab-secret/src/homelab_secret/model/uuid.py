from __future__ import annotations

import typing

import pulumi_random as random
from pulumi import ResourceOptions

from . import SecretModel

if typing.TYPE_CHECKING:
    from ..resource import SecretResource


class SecretUuidModel(SecretModel):
    uuid: None

    def build_resource(
        self, resource_name: str, opts: ResourceOptions, resource: SecretResource | None
    ) -> random.RandomUuid:
        opts = self.opts(opts)
        return random.RandomUuid(resource_name, opts=opts)
