from __future__ import annotations

import typing

from homelab_network.resource.network import NetworkResource
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions
from pydantic import HttpUrl

from .hostname import KeepassEntryHostnameModel
from .password import KeepassEntryPasswordModel
from .username import KeepassEntryUsernameModel

if typing.TYPE_CHECKING:
    from ...resource.keepass.entry import KeeypassEntryResource


class KeepassEntryModel(HomelabBaseModel):
    username: KeepassEntryUsernameModel = KeepassEntryUsernameModel()
    password: KeepassEntryPasswordModel = KeepassEntryPasswordModel()
    hostname: KeepassEntryHostnameModel
    urls: list[HttpUrl] = []
    apps: list[str] = []

    def build_resource(
        self, *, opts: ResourceOptions, network_resource: NetworkResource
    ) -> KeeypassEntryResource:
        from ...resource.keepass.entry import KeeypassEntryResource

        return KeeypassEntryResource(self, opts=opts, network_resource=network_resource)
