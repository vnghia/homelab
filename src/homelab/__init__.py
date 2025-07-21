import json_fix as json_fix
from homelab_backup_service import BackupService
from homelab_balite_service import BaliteService
from homelab_barman_service import BarmanService
from homelab_config import Config
from homelab_crowdsec_service import CrowdsecService
from homelab_dagu_service import DaguService
from homelab_ddns_service import DdnsService
from homelab_docker.config import DockerConfig
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from homelab_frp_service import FrpService
from homelab_gluetun_service import GluetunService
from homelab_kanidm_service import KanidmService
from homelab_network.resource.network import NetworkResource
from homelab_ntfy_service import NtfyService
from homelab_restic_service import ResticService
from homelab_secret.resource.keepass import KeepassResource
from homelab_tailscale_service import TailscaleService
from homelab_traefik_service import TraefikService

from .docker import Docker
from .file import File
from .service.config import ServiceConfig


class Homelab:
    def __init__(self) -> None:
        self.config = Config[ServiceConfig].build(DockerConfig[ServiceConfig])
        self.project_prefix = Config.get_name(None, project=True, stack=True)
        self.docker = Docker(self.config, self.project_prefix)

        self.tailscale = TailscaleService(
            self.docker.services_config.tailscale,
            opts=None,
            hostname=self.project_prefix,
            internal_aliases=self.config.network.aliases,
            docker_resource_args=self.docker.resource_args,
        )

        self.network = NetworkResource(
            self.config.network,
            opts=None,
            private_ips=self.tailscale.ips,
            project_prefix=self.project_prefix,
        )
        self.docker.resource_args.hostnames |= self.network.hostnames

        self.gluetun = GluetunService(
            self.docker.services_config.gluetun,
            opts=None,
            docker_resource_args=self.docker.resource_args,
        )

        self.crowdsec = CrowdsecService(
            self.docker.services_config.crowdsec,
            opts=None,
            docker_resource_args=self.docker.resource_args,
        )
        self.traefik = TraefikService(
            self.docker.services_config.traefik,
            opts=None,
            network_resource=self.network,
            docker_resource_args=self.docker.resource_args,
        )
        self.ddns = DdnsService(
            self.docker.services_config.ddns,
            opts=None,
            network_resource=self.network,
            docker_resource_args=self.docker.resource_args,
        )
        self.frp = FrpService(
            self.docker.services_config.frp,
            opts=None,
            network_resource=self.network,
            docker_resource_args=self.docker.resource_args,
        )

        self.kanidm = KanidmService(
            self.docker.services_config.kanidm,
            opts=None,
            docker_resource_args=self.docker.resource_args,
        )
        self.ntfy = NtfyService(
            self.docker.services_config.ntfy,
            opts=None,
            docker_resource_args=self.docker.resource_args,
        )
        self.dagu = DaguService(
            self.docker.services_config.dagu,
            opts=None,
            docker_resource_args=self.docker.resource_args,
        )

        self.extra_services = {
            service: type(
                "{}Service".format(service.capitalize()), (ExtraService,), {}
            )(model, opts=None, docker_resource_args=self.docker.resource_args).build()
            for service, model in ExtraService.sort_depends_on(
                self.docker.services_config.extra(ServiceWithConfigModel[ExtraConfig])
            ).items()
        }

        # It should always be the last service
        self.barman = BarmanService(
            self.docker.services_config.barman,
            opts=None,
            backup_config=self.docker.services_config.backup.config,
            docker_resource_args=self.docker.resource_args,
        )
        self.balite = BaliteService(
            self.docker.services_config.balite,
            opts=None,
            backup_config=self.docker.services_config.backup.config,
            docker_resource_args=self.docker.resource_args,
        )

        self.restic = ResticService(
            self.docker.services_config.restic,
            opts=None,
            hostname=self.project_prefix,
            backup_config=self.docker.services_config.backup.config,
            barman_service=self.barman,
            balite_service=self.balite,
            docker_resource_args=self.docker.resource_args,
        )

        self.keepass = KeepassResource(
            {
                service.add_service_name(name): resource
                for service in ServiceResourceBase.SERVICES.values()
                if service._keepass
                for name, resource in service._keepass.keepasses.items()
            }
        )

        self.file = File(traefik_service=self.traefik, dagu_service=self.dagu)

        self.backup = BackupService(
            self.docker.services_config.backup,
            opts=None,
            dagu_service=self.dagu,
            restic_service=self.restic,
            docker_resource_args=self.docker.resource_args,
        )
