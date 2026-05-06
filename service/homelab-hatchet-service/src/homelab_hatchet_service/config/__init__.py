from homelab_extra_service.config import ExtraConfig
from homelab_extract import GlobalExtract


class HatchetConfig(ExtraConfig):
    workflow_dir: GlobalExtract
    docker_dir: GlobalExtract
