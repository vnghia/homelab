from __future__ import annotations

import typing

from homelab_secret.resource.keepass.entry import KeepassEntryResource
from pulumi import ComponentResource, ResourceOptions

from ...config.service.keepass import ServiceKeepassConfig

if typing.TYPE_CHECKING:
    from ...resource.service import ServiceResourceBase


class ServiceKeepassResouse(ComponentResource):
    RESOURCE_NAME = "keepass"

    def __init__(
        self,
        config: ServiceKeepassConfig,
        *,
        opts: ResourceOptions,
        main_service: ServiceResourceBase,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, main_service.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.keepasses = {
            name: model.build_resource(
                main_service.add_service_name(name),
                opts=self.child_opts,
                hostnames=main_service.docker_resource_args.hostnames,
            )
            for name, model in config.root.items()
        }

        self.register_outputs({})

    def __getitem__(self, key: str | None) -> KeepassEntryResource:
        return self.keepasses[key]
