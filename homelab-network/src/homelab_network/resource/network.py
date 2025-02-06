from typing import Mapping

from pulumi import ComponentResource, Input, ResourceOptions
from pydantic import IPvAnyAddress

from homelab_network.config.network import NetworkConfig

from .record import RecordResource


class NetworkResource(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions | None,
        private_ips: Mapping[str, Input[IPvAnyAddress]],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.public = RecordResource(
            "public", config.public, opts=self.child_opts, ips=config.public_ips
        )
        self.private = RecordResource(
            "private", config.private, opts=self.child_opts, ips=private_ips
        )

        self.register_outputs({})
