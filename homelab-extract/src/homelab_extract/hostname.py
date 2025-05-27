from homelab_network.resource.network import Hostnames
from homelab_pydantic import HomelabBaseModel


class GlobalExtractHostnameSource(HomelabBaseModel):
    hostname: str
    public: bool
    scheme: str | None = None
    append_slash: bool = False

    def to_hostname(self, hostnames: Hostnames) -> str:
        hostname = hostnames[self.public][self.hostname]
        if self.scheme:
            hostname = "{}://{}{}".format(
                self.scheme, hostname, "/" if self.append_slash else ""
            )
        return hostname
