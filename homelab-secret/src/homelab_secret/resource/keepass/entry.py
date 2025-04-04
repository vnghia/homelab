from typing import Any

from homelab_network.resource.network import Hostnames
from pulumi import ComponentResource, Output, ResourceOptions

from ...model.keepass.entry import KeepassEntryModel


class KeepassEntryResource(ComponentResource):
    def __init__(
        self,
        resource_name: str,
        model: KeepassEntryModel,
        *,
        opts: ResourceOptions,
        hostnames: Hostnames,
    ) -> None:
        super().__init__(resource_name, resource_name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.model = model
        self.username = self.model.username.to_username(
            opts=self.child_opts, hostnames=hostnames
        )
        self.password = self.model.password.to_password(opts=self.child_opts)
        self.hostname = self.model.hostname.__replace__(scheme="https").to_hostname(
            hostnames
        )

        self.register_outputs({})

    def to_props(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "password": self.password,
            "hostname": self.hostname,
            "urls": self.model.urls,
            "apps": self.model.apps,
        }
