from homelab_docker.model.service import ServiceWithConfigModel
from homelab_kanidm_service.config import KandimConfig

from ..config import HostServiceConfig


class SunServiceConfig(HostServiceConfig):
    kanidm: ServiceWithConfigModel[KandimConfig]
