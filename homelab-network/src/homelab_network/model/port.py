from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class NetworkPortModel(HomelabBaseModel):
    http: PositiveInt
    https: PositiveInt
