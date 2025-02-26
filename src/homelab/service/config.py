from homelab_backup.config import BackupConfig
from homelab_barman_service.config import BarmanConfig
from homelab_dagu_service.config import DaguConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceModel, ServiceWithConfigModel
from homelab_restic_service.config import ResticConfig
from homelab_traefik_service.config import TraefikConfig


class ServiceConfig(ServiceConfigBase):
    tailscale: ServiceModel
    traefik: ServiceWithConfigModel[TraefikConfig]
    dagu: ServiceWithConfigModel[DaguConfig]
    barman: ServiceWithConfigModel[BarmanConfig]
    restic: ServiceWithConfigModel[ResticConfig]
    backup: ServiceWithConfigModel[BackupConfig]
