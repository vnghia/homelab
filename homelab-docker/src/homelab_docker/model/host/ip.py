from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabServiceConfigDict
from pydantic import IPvAnyAddress


class HostReachableIpModel(HomelabServiceConfigDict[IPvAnyAddress]):
    NONE_KEY = "reachable"

    root: dict[str | None, IPvAnyAddress] = {}


class HostIpModel(HomelabBaseModel):
    external: IPvAnyAddress
    reachable: HostReachableIpModel = HostReachableIpModel({})

    def get_ip(self, node: str) -> IPvAnyAddress:
        return (
            self.reachable.root.get(node)
            or self.reachable.root.get(None)
            or self.external
        )
