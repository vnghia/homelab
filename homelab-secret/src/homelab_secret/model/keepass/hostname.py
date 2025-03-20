from homelab_network.resource.network import Hostnames
from homelab_pydantic import HomelabBaseModel
from pulumi import Output


class KeepassEntryHostnameModel(HomelabBaseModel):
    hostname: str
    public: bool

    def to_hostname(self, hostnames: Hostnames) -> Output[str]:
        return hostnames[self.public][self.hostname]
