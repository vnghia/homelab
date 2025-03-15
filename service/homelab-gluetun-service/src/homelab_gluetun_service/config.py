from homelab_docker.extract.service import ServiceExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class GluetunConfig(HomelabBaseModel):
    opvn: str | None = None
    opvn_path: ServiceExtract
    forwarding_ports: list[PositiveInt] = []
