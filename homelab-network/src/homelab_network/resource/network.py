from typing import Mapping

from pulumi import ComponentResource, Input, Output, ResourceOptions
from pydantic import IPvAnyAddress

from homelab_network.config.network import NetworkConfig

from .record import RecordResource
from .token import TokenResource


class Hostnames(dict[bool, dict[str, Output[str]]]):
    pass


class NetworkResource(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions | None,
        private_ips: Mapping[str, Input[IPvAnyAddress]],
        project_prefix: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.public = RecordResource(
            "public", config.public, opts=self.child_opts, ips=config.public_ips
        )
        self.private = RecordResource(
            "private", config.private, opts=self.child_opts, ips=private_ips
        )
        self.token = TokenResource(
            config, opts=self.child_opts, project_prefix=project_prefix
        )

        self.register_outputs({})

    @property
    def hostnames(self) -> Hostnames:
        return Hostnames({True: self.public.hostnames, False: self.private.hostnames})
