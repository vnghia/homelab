from typing import Any

from homelab_extra_service.config import ExtraConfig
from homelab_extract.service import ServiceExtract


class PydioConfig(ExtraConfig):
    install: Any
    install_path: ServiceExtract
