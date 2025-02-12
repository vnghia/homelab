from homelab_backup_service.service import BackupService
from homelab_config import Config
from homelab_dagu_service import DaguService
from homelab_docker.config.docker import DockerConfig
from homelab_docker.resource.database.global_ import DatabaseGlobalResource
from homelab_dozzle_service import DozzleService
from homelab_network.resource.network import NetworkResource
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
            container_model_global_args=self.docker.container_model_global_args,
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
            container_model_global_args=self.docker.container_model_global_args,
            tailscale_service=self.tailscale,
        )
        self.dozzle = DozzleService(
            self.docker.services_config.dozzle,
            opts=None,
            container_model_global_args=self.docker.container_model_global_args,
            traefik_static_config=self.traefik.static,
        )
        self.nghe = NgheService(
            self.docker.services_config.nghe,
            opts=None,
            s3_integration_config=self.config.integration.s3,
            container_model_global_args=self.docker.container_model_global_args,
            traefik_static_config=self.traefik.static,
        )
        self.memos = MemosService(
            self.docker.services_config.memos,
            opts=None,
            container_model_global_args=self.docker.container_model_global_args,
            traefik_static_config=self.traefik.static,
        )
        self.dagu = DaguService(
            self.docker.services_config.dagu,
            opts=None,
            s3_integration_config=self.config.integration.s3,
            container_model_global_args=self.docker.container_model_global_args,
            traefik_static_config=self.traefik.static,
        )

        # It should always be the last service
        self.backup = BackupService(
            self.docker.services_config.backup,
            opts=None,
            volume_config=self.docker.config.volumes,
            dagu_service=self.dagu,
            container_model_global_args=self.docker.container_model_global_args,
        )
