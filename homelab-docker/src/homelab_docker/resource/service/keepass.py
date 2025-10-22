from __future__ import annotations

import typing

from homelab_secret.resource.keepass.entry import KeepassEntryResource
from pulumi import ComponentResource, ResourceOptions

from ...config.service.keepass import ServiceKeepassConfig

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class ServiceKeepassResource(ComponentResource):
    RESOURCE_NAME = "keepass"

    def __init__(
        self,
        config: ServiceKeepassConfig,
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, extractor_args.service.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.keepasses = {
            name: model.build_resource(
                extractor_args.service.add_service_name(name),
                opts=self.child_opts,
                hostnames=extractor_args.hostnames,
            )
            for name, model in config.root.items()
        }

        self.register_outputs({})

    def __getitem__(self, key: str | None) -> KeepassEntryResource:
        return self.keepasses[key]
