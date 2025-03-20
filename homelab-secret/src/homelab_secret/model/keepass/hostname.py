from homelab_network.resource.network import NetworkResource
from homelab_pydantic import HomelabBaseModel
from pulumi import Output


class KeepassEntryHostnameModel(HomelabBaseModel):
    hostname: str
    public: bool

    def to_hostname(self, network_resource: NetworkResource) -> Output[str]:
        return network_resource.hostnames[self.public][self.hostname]
