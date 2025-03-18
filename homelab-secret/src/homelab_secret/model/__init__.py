from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class SecretModel(HomelabBaseModel):
    length: PositiveInt = 64
    special: bool | None = None
    protect: bool = False
