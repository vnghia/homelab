from typing import Any

from homelab_extract.plain import PlainArgs
from pulumi import ComponentResource, ResourceOptions

from ...model.keepass.entry import KeepassEntryModel


class KeepassEntryResource(ComponentResource):
    def __init__(
        self,
        resource_name: str,
        model: KeepassEntryModel,
        *,
        opts: ResourceOptions,
        plain_args: PlainArgs,
    ) -> None:
        super().__init__(resource_name, resource_name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.plain_args = plain_args
        self.model = model
        self.username = self.model.username.to_username(
            opts=self.child_opts, plain_args=self.plain_args
        )
        self.password = self.model.password.to_password(
            opts=self.child_opts, plain_args=self.plain_args
        )
        self.hostname = self.model.hostname.__replace__(scheme="https").to_url(
            self.plain_args
        )

        self.register_outputs({})

    def to_props(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "password": self.password.result,
            "hostname": self.hostname,
            "urls": [url.extract_str(self.plain_args) for url in self.model.urls],
            "apps": self.model.apps,
        }
