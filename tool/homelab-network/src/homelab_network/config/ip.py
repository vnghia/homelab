from homelab_pydantic import HomelabRootModel

from ..model.ip import NetworkIpModel, NetworkIpSource


class NetworkIpConfig(HomelabRootModel[NetworkIpModel | NetworkIpSource]):
    pass
