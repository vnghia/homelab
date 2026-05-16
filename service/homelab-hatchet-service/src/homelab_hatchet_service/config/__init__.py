from homelab_extra_service.config import ExtraConfig
from homelab_extract import GlobalExtract


class HatchetConfig(ExtraConfig):
    worker: str
    workflow_dir: GlobalExtract
    docker_dir: GlobalExtract
    schedule_dir: GlobalExtract
    config_dir: GlobalExtract
    scheduler_dir: GlobalExtract
