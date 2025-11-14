from __future__ import annotations

import typing

import pulumi_random as random
from homelab_extract.plain import PlainArgs
from pulumi import ResourceOptions
from pydantic import PositiveInt

from .base import SecretBaseModel

if typing.TYPE_CHECKING:
    from ..resource import SecretResource


class SecretPasswordModel(SecretBaseModel):
    length: PositiveInt = 64
    special: bool | None = None
    upper: bool | None = None

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource | None,
        plain_args: PlainArgs,
    ) -> random.RandomPassword:
        opts = self.opts(opts)
        return random.RandomPassword(
            resource_name,
            opts=opts,
            length=self.length,
            special=self.special,
            upper=self.upper,
        )
