from homelab_backup_service.config import BackupConfig
from homelab_balite_service.config import BaliteConfig
from homelab_barman_service.config import BarmanConfig
from homelab_dagu_service.config import DaguConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceModel, ServiceWithConfigModel
from homelab_litestream_service.config import LitestreamConfig
from homelab_restic_service.config import ResticConfig
from homelab_traefik_service.config import TraefikConfig


class HostServiceConfig(ServiceConfigBase):
    tailscale: ServiceModel
    traefik: ServiceWithConfigModel[TraefikConfig]
    dagu: ServiceWithConfigModel[DaguConfig]
    backup: ServiceWithConfigModel[BackupConfig]
    barman: ServiceWithConfigModel[BarmanConfig]
    balite: ServiceWithConfigModel[BaliteConfig]
    litestream: ServiceWithConfigModel[LitestreamConfig]
    restic: ServiceWithConfigModel[ResticConfig]
