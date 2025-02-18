import json_fix  # noqa
from homelab_backup_service import BackupService
from homelab_barman_service import BarmanService
from homelab_config import Config
from homelab_dagu_service import DaguService
from homelab_docker.config import DockerConfig
from homelab_docker.resource.database.global_ import DatabaseGlobalResource
from homelab_dozzle_service import DozzleService
from homelab_network.resource.network import NetworkResource
from homelab_restic_service import ResticService
from homelab_tailscale_service import TailscaleService
from homelab_traefik_service import TraefikService

from .docker import Docker
from .service.config import ServiceConfig
from .service.memos import MemosService
from .service.nghe import NgheService


class Homelab:
    def __init__(self) -> None:
        self.config = Config[ServiceConfig].build(DockerConfig[ServiceConfig])
        self.project_prefix = Config.get_name(None, project=True, stack=True)
        self.docker = Docker(self.config, self.project_prefix)

        self.datbase_global = DatabaseGlobalResource(
            opts=None, volume_resource=self.docker.resource.volume
        )

        self.tailscale = TailscaleService(
            self.docker.services_config.tailscale,
            opts=None,
            hostname=self.project_prefix,
            docker_resource_args=self.docker.resource_args,
        )

        self.network = NetworkResource(
            self.config.network,
            opts=None,
            private_ips=self.tailscale.ips,
            project_prefix=self.project_prefix,
        )

        self.traefik = TraefikService(
            self.docker.services_config.traefik,
            opts=None,
            network_resource=self.network,
            tailscale_service=self.tailscale,
            docker_resource_args=self.docker.resource_args,
        )
        self.dozzle = DozzleService(
            self.docker.services_config.dozzle,
            opts=None,
            traefik_service=self.traefik,
            docker_resource_args=self.docker.resource_args,
        )
        self.nghe = NgheService(
            self.docker.services_config.nghe,
            opts=None,
            traefik_service=self.traefik,
            docker_resource_args=self.docker.resource_args,
        )
        self.memos = MemosService(
            self.docker.services_config.memos,
            opts=None,
            traefik_service=self.traefik,
            docker_resource_args=self.docker.resource_args,
        )
        self.dagu = DaguService(
            self.docker.services_config.dagu,
            opts=None,
            traefik_service=self.traefik,
            docker_resource_args=self.docker.resource_args,
        )

        # It should always be the last service
        self.barman = BarmanService(
            self.docker.services_config.barman,
            opts=None,
            dagu_service=self.dagu,
            docker_resource_args=self.docker.resource_args,
        )
        self.restic = ResticService(
            self.docker.services_config.restic,
            opts=None,
            volume_config=self.config.docker.volumes,
            dagu_service=self.dagu,
            docker_resource_args=self.docker.resource_args,
        )
        self.backup = BackupService(
            self.docker.services_config.backup,
            opts=None,
            volume_config=self.docker.config.volumes,
            dagu_service=self.dagu,
            docker_resource_args=self.docker.resource_args,
        )
