from __future__ import annotations

import dataclasses
import typing
from uuid import UUID

import pulumi_random as random
from homelab_extract.plain import PlainArgs
from pulumi import Output, ResourceOptions

from .base import SecretBaseModel

if typing.TYPE_CHECKING:
    from ..resource import SecretResource


@dataclasses.dataclass
class SensitiveUuid:
    result: Output[str]


class SecretUuidModel(SecretBaseModel):
    uuid: None

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions,
        resource: SecretResource | None,
        plain_args: PlainArgs,
    ) -> SensitiveUuid:
        opts = self.opts(opts)
        return SensitiveUuid(
            random.RandomBytes(resource_name, length=16).hex.apply(
                lambda x: str(UUID(x))
            )
        )
