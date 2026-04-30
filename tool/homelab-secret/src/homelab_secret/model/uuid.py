from __future__ import annotations

import typing
from uuid import UUID

import pulumi_random as random
from homelab_extract.plain import PlainArgs
from pulumi import ResourceOptions

from .base import SecretBaseModel, SecretOutput

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
    ) -> SecretOutput:
        opts = self.opts(opts)
        return SecretOutput(
            random.RandomBytes(resource_name, length=16).hex.apply(
                lambda x: str(UUID(x))
            )
        )
