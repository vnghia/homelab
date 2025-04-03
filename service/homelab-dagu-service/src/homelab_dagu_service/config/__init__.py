from homelab_extra_service.config import ExtraConfig
from homelab_extract.service import ServiceExtract


class DaguConfig(ExtraConfig):
    dags_dir: ServiceExtract
    log_dir: ServiceExtract
