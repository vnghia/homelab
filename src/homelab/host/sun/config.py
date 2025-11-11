from homelab_backup_service.config import BackupConfig
from homelab_balite_service.config import BaliteConfig
from homelab_barman_service.config import BarmanConfig
from homelab_ddns_service.config import DdnsConfig
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_kanidm_service.config import KandimConfig
from homelab_restic_service.config import ResticConfig

from ..config import HostServiceConfig


class SunServiceConfig(HostServiceConfig):
    ddns: ServiceWithConfigModel[DdnsConfig]
    kanidm: ServiceWithConfigModel[KandimConfig]
    barman: ServiceWithConfigModel[BarmanConfig]
    balite: ServiceWithConfigModel[BaliteConfig]
    restic: ServiceWithConfigModel[ResticConfig]
    backup: ServiceWithConfigModel[BackupConfig]
