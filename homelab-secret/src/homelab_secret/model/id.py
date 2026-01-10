from __future__ import annotations

import typing

import pulumi_random as random
from homelab_extract.plain import PlainArgs
from pulumi import ResourceOptions
from pydantic import PositiveInt

from .base import SecretBaseModel, SecretOutput

if typing.TYPE_CHECKING:
    from ..resource import SecretResource


class SecretIdModel(SecretBaseModel):
    id: None
    length: PositiveInt = 4
    secure: bool = False

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource | None,
        plain_args: PlainArgs,
    ) -> SecretOutput:
        opts = self.opts(opts)
        if self.secure:
            return SecretOutput(
                random.RandomBytes(resource_name, length=self.length).hex
            )
        return SecretOutput(random.RandomId(resource_name, byte_length=self.length).hex)
