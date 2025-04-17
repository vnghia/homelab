from homelab_apprise_service.config import AppriseConfig
from homelab_backup_service.config import BackupConfig
from homelab_barman_service.config import BarmanConfig
from homelab_crowdsec_service.config import CrowdsecConfig
from homelab_dagu_service.config import DaguConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceModel, ServiceWithConfigModel
from homelab_extra_service.config import ExtraConfig
from homelab_gluetun_service.config import GluetunConfig
from homelab_kanidm_service.config import KandimConfig
from homelab_restic_service.config import ResticConfig
from homelab_seafile_service.config import SeafileConfig
from homelab_sqlite_backup_service.config import SqliteBackupConfig
from homelab_traefik_service.config import TraefikConfig


class ServiceConfig(ServiceConfigBase):
    tailscale: ServiceModel
    traefik: ServiceWithConfigModel[TraefikConfig]
    gluetun: ServiceWithConfigModel[GluetunConfig]
    crowdsec: ServiceWithConfigModel[CrowdsecConfig]
    kanidm: ServiceWithConfigModel[KandimConfig]
    ntfy: ServiceWithConfigModel[ExtraConfig]
    apprise: ServiceWithConfigModel[AppriseConfig]
    dagu: ServiceWithConfigModel[DaguConfig]
    seafile: ServiceWithConfigModel[SeafileConfig]
    barman: ServiceWithConfigModel[BarmanConfig]
    sqlite_backup: ServiceWithConfigModel[SqliteBackupConfig]
    restic: ServiceWithConfigModel[ResticConfig]
    backup: ServiceWithConfigModel[BackupConfig]
