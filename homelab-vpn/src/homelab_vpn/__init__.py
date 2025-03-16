from homelab_docker.extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class VpnConfig(HomelabBaseModel):
    container: GlobalExtract
    ports: dict[str, PositiveInt] = {}
