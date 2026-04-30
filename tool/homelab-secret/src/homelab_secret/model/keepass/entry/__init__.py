from __future__ import annotations

import typing

from homelab_extract.plain import GlobalPlainExtractSource, PlainArgs
from homelab_extract.plain.hostname import GlobalPlainExtractHostnameSource
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions

from .password import KeepassEntryPasswordModel
from .username import KeepassEntryUsernameModel

if typing.TYPE_CHECKING:
    from ....resource.keepass.entry import KeepassEntryResource


class KeepassEntryModel(HomelabBaseModel):
    username: KeepassEntryUsernameModel = KeepassEntryUsernameModel()
    password: KeepassEntryPasswordModel = KeepassEntryPasswordModel()
    hostname: GlobalPlainExtractHostnameSource
    urls: list[GlobalPlainExtractSource] = []
    apps: list[str] = []

    def build_resource(
        self, resource_name: str, *, opts: ResourceOptions, plain_args: PlainArgs
    ) -> KeepassEntryResource:
        from ....resource.keepass.entry import KeepassEntryResource

        return KeepassEntryResource(
            resource_name, self, opts=opts, plain_args=plain_args
        )
