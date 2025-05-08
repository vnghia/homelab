from homelab_pydantic import HomelabBaseModel

from ..model.port import NetworkPortModel


class NetworkPortConfig(HomelabBaseModel):
    internal: NetworkPortModel
    external: NetworkPortModel
