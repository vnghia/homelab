from homelab_docker.extract.service import ServiceExtract
from homelab_pydantic import HomelabBaseModel


class GluetunConfig(HomelabBaseModel):
    opvn: str | None = None
    opvn_path: ServiceExtract
