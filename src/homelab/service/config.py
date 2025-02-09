from homelab_backup_service.config.backup import BackupConfig
from homelab_docker.config.database import DatabaseConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceModel
from homelab_traefik_service.config import TraefikConfig

from .nghe.config import NgheConfig


class ServiceConfig(ServiceConfigBase):
    tailscale: ServiceModel[None]
    traefik: ServiceModel[TraefikConfig]
    dozzle: ServiceModel[None]
    nghe: ServiceModel[NgheConfig]
    memos: ServiceModel[None]
    dagu: ServiceModel[None]
    backup: ServiceModel[BackupConfig]

    @property
    def databases(self) -> dict[str, DatabaseConfig]:
        return {
            field: service.databases
            for field, service in self
            if isinstance(service, ServiceModel) and service.databases
        }
