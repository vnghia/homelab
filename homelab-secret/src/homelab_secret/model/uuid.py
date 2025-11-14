from __future__ import annotations

import typing

import pulumi_random as random
from homelab_extract.plain import PlainArgs
from pulumi import ResourceOptions

from .base import SecretBaseModel

if typing.TYPE_CHECKING:
    from ..resource import SecretResource


class SecretUuidModel(SecretBaseModel):
    uuid: None

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource | None,
        plain_args: PlainArgs,
    ) -> random.RandomUuid:
        opts = self.opts(opts)
        return random.RandomUuid(resource_name, opts=opts)
