from homelab_pydantic import HomelabBaseModel
from pydantic import IPvAnyAddress


class HostDatacenterModel(HomelabBaseModel):
    name: str
    ip: IPvAnyAddress
