from homelab_ddns_service.config import DdnsConfig
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_kanidm_service.config import KandimConfig

from ..config import HostServiceConfig


class SunServiceConfig(HostServiceConfig):
    ddns: ServiceWithConfigModel[DdnsConfig]
    kanidm: ServiceWithConfigModel[KandimConfig]
