from homelab_global import GlobalArgs
from pulumi import ComponentResource, ResourceOptions

from ..config import NetworkConfig
from ..model.hostname import Hostnames
from .token import TokenResource


class NetworkResource(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions | None,
        global_args: GlobalArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config

        self.token = TokenResource(
            config, opts=self.child_opts, global_args=global_args
        )

        self.register_outputs({})

    @property
    def hostnames(self) -> Hostnames:
        return Hostnames(
            {key: record.hostnames for key, record in self.config.records.items()}
        )
