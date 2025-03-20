from __future__ import annotations

import typing

from homelab_network.resource.network import Hostnames
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions
from pydantic import HttpUrl

from .hostname import KeepassEntryHostnameModel
from .password import KeepassEntryPasswordModel
from .username import KeepassEntryUsernameModel

if typing.TYPE_CHECKING:
    from ...resource.keepass.entry import KeepassEntryResource


class KeepassEntryModel(HomelabBaseModel):
    username: KeepassEntryUsernameModel = KeepassEntryUsernameModel()
    password: KeepassEntryPasswordModel = KeepassEntryPasswordModel()
    hostname: KeepassEntryHostnameModel
    urls: list[HttpUrl] = []
    apps: list[str] = []

    def build_resource(
        self, resource_name: str, *, opts: ResourceOptions, hostnames: Hostnames
    ) -> KeepassEntryResource:
        from ...resource.keepass.entry import KeepassEntryResource

        return KeepassEntryResource(resource_name, self, opts=opts, hostnames=hostnames)
