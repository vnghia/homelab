from homelab_docker.model.service.extract import ServiceExtract
from homelab_pydantic import HomelabBaseModel


class DaguConfig(HomelabBaseModel):
    dags_dir: ServiceExtract
    log_dir: ServiceExtract
