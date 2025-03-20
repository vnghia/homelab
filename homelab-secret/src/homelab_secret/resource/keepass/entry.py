from homelab_network.resource.network import NetworkResource
from pulumi import ComponentResource, ResourceOptions

from ...model.keepass.entry import KeepassEntryModel


class KeeypassEntryResource(ComponentResource):
    RESOURCE_NAME = "entry"

    def __init__(
        self,
        model: KeepassEntryModel,
        *,
        opts: ResourceOptions,
        network_resource: NetworkResource,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.model = model
        self.username = self.model.username.to_username(opts=self.child_opts)
        self.password = self.model.password.to_password(opts=self.child_opts)
        self.hostname = self.model.hostname.to_hostname(network_resource)
