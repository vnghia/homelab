from homelab_network.model.hostname import Hostnames
from homelab_pydantic import HomelabBaseModel


class GlobalExtractHostnameSource(HomelabBaseModel):
    hostname: str
    record: str
    scheme: str | None = None
    append_slash: bool = False

    def to_hostname(self, hostnames: Hostnames) -> str:
        hostname = hostnames[self.record][self.hostname].value
        if self.scheme:
            hostname = "{}://{}{}".format(
                self.scheme, hostname, "/" if self.append_slash else ""
            )
        return hostname
