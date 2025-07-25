from homelab_backup_service.config import BackupConfig
from homelab_balite_service.config import BaliteConfig
from homelab_barman_service.config import BarmanConfig
from homelab_crowdsec_service.config import CrowdsecConfig
from homelab_dagu_service.config import DaguConfig
from homelab_ddns_service.config import DdnsConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceModel, ServiceWithConfigModel
from homelab_extra_service.config import ExtraConfig
from homelab_gluetun_service.config import GluetunConfig
from homelab_kanidm_service.config import KandimConfig
from homelab_restic_service.config import ResticConfig
from homelab_traefik_service.config import TraefikConfig


class ServiceConfig(ServiceConfigBase):
    tailscale: ServiceModel
    ddns: ServiceWithConfigModel[DdnsConfig]
    traefik: ServiceWithConfigModel[TraefikConfig]
    gluetun: ServiceWithConfigModel[GluetunConfig]
    crowdsec: ServiceWithConfigModel[CrowdsecConfig]
    kanidm: ServiceWithConfigModel[KandimConfig]
    ntfy: ServiceWithConfigModel[ExtraConfig]
    dagu: ServiceWithConfigModel[DaguConfig]
    barman: ServiceWithConfigModel[BarmanConfig]
    balite: ServiceWithConfigModel[BaliteConfig]
    restic: ServiceWithConfigModel[ResticConfig]
    backup: ServiceWithConfigModel[BackupConfig]
