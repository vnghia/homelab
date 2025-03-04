from homelab_docker.extract.service import ServiceExtract
from homelab_extra_service.config import ExtraConfig


class DaguConfig(ExtraConfig):
    dags_dir: ServiceExtract
    log_dir: ServiceExtract
