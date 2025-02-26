import json_fix as json_fix
from homelab_backup_service import BackupService
from homelab_barman_service import BarmanService
from homelab_config import Config
from homelab_dagu_service import DaguService
from homelab_docker.config import DockerConfig
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.database import DatabaseResource
from homelab_dozzle_service import DozzleService
from homelab_network.resource.network import NetworkResource
from homelab_restic_service import ResticService
from homelab_tailscale_service import TailscaleService
from homelab_traefik_service import TraefikService

from .docker import Docker
from .service.config import ServiceConfig
from .service.extra import ExtraConfig, ExtraService
from .service.nghe import NgheService


class Homelab:
    def __init__(self) -> None:
        self.config = Config[ServiceConfig].build(DockerConfig[ServiceConfig])
        self.project_prefix = Config.get_name(None, project=True, stack=True)
        self.docker = Docker(self.config, self.project_prefix)

        self.datbase_global = DatabaseResource(
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
        self.dagu = DaguService(
            self.docker.services_config.dagu,
            opts=None,
            traefik_service=self.traefik,
            docker_resource_args=self.docker.resource_args,
        )

        self.extra_services = {
            service: type(
                "{}Service".format(service.capitalize()), (ExtraService,), {}
            )(
                model,
                opts=None,
                traefik_service=self.traefik,
                docker_resource_args=self.docker.resource_args,
            )
            for service, model in self.docker.services_config.extra(
                ServiceWithConfigModel[ExtraConfig]
            ).items()
        }

        # It should always be the last service
        self.barman = BarmanService(
            self.docker.services_config.barman,
            opts=None,
            backup_config=self.docker.services_config.backup.config,
            dagu_service=self.dagu,
            docker_resource_args=self.docker.resource_args,
        )
        self.restic = ResticService(
            self.docker.services_config.restic,
            opts=None,
            hostname=self.project_prefix,
            backup_config=self.docker.services_config.backup.config,
            dagu_service=self.dagu,
            docker_resource_args=self.docker.resource_args,
        )
        self.backup = BackupService(
            self.docker.services_config.backup,
            opts=None,
            dagu_service=self.dagu,
            barman_service=self.barman,
            restic_service=self.restic,
            docker_resource_args=self.docker.resource_args,
        )
