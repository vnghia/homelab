from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class VpnConfig(HomelabBaseModel):
    service: str
    container: str | None = None
    ports: dict[str, PositiveInt] = {}
