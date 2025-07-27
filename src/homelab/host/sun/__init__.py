from homelab_backup_service import BackupService
from homelab_balite_service import BaliteService
from homelab_barman_service import BarmanService
from homelab_crowdsec_service import CrowdsecService
from homelab_dagu_service import DaguService
from homelab_ddns_service import DdnsService
from homelab_docker.config import DockerConfig
from homelab_gluetun_service import GluetunService
from homelab_kanidm_service import KanidmService
from homelab_network.resource.network import NetworkResource
from homelab_ntfy_service import NtfyService
from homelab_restic_service import ResticService
from homelab_tailscale_service import TailscaleService
from homelab_traefik_service import TraefikService
from pulumi import ResourceOptions

from ...file import File
from .. import HostBase
from .config import SunServiceConfig


class SunHost(HostBase[SunServiceConfig]):
    def __init__(
        self,
        config: DockerConfig[SunServiceConfig],
        *,
        opts: ResourceOptions | None,
        project_prefix: str,
        network_resource: NetworkResource,
    ) -> None:
        super().__init__(
            config,
            opts=opts,
            project_prefix=project_prefix,
            network_resource=network_resource,
        )

        self.tailscale = TailscaleService(
            self.docker.services_config.tailscale,
            opts=self.child_opts,
            hostname=self.project_prefix,
            internal_aliases=self.network.config.aliases,
            docker_resource_args=self.docker.resource_args,
        )

        self.gluetun = GluetunService(
            self.docker.services_config.gluetun,
            opts=self.child_opts,
            docker_resource_args=self.docker.resource_args,
        )

        self.crowdsec = CrowdsecService(
            self.docker.services_config.crowdsec,
            opts=self.child_opts,
            docker_resource_args=self.docker.resource_args,
        )
        self.traefik = TraefikService(
            self.docker.services_config.traefik,
            opts=self.child_opts,
            network_resource=self.network,
            docker_resource_args=self.docker.resource_args,
        )
        self.ddns = DdnsService(
            self.docker.services_config.ddns,
            opts=self.child_opts,
            network_resource=self.network,
            docker_resource_args=self.docker.resource_args,
        )

        self.dagu = DaguService(
            self.docker.services_config.dagu,
            opts=self.child_opts,
            docker_resource_args=self.docker.resource_args,
        )
        self.kanidm = KanidmService(
            self.docker.services_config.kanidm,
            opts=self.child_opts,
            docker_resource_args=self.docker.resource_args,
        )
        self.ntfy = NtfyService(
            self.docker.services_config.ntfy,
            opts=self.child_opts,
            docker_resource_args=self.docker.resource_args,
        )

        self.build_extra_services()

        # It should always be the last service
        self.barman = BarmanService(
            self.docker.services_config.barman,
            opts=self.child_opts,
            backup_config=self.docker.services_config.backup.config,
            docker_resource_args=self.docker.resource_args,
        )

        self.balite = BaliteService(
            self.docker.services_config.balite,
            opts=self.child_opts,
            backup_config=self.docker.services_config.backup.config,
            docker_resource_args=self.docker.resource_args,
        )

        self.restic = ResticService(
            self.docker.services_config.restic,
            opts=self.child_opts,
            hostname=self.project_prefix,
            backup_config=self.docker.services_config.backup.config,
            barman_service=self.barman,
            balite_service=self.balite,
            docker_resource_args=self.docker.resource_args,
        )

        self.file = File(
            opts=self.child_opts, traefik_service=self.traefik, dagu_service=self.dagu
        )

        self.backup = BackupService(
            self.docker.services_config.backup,
            opts=self.child_opts,
            dagu_service=self.dagu,
            restic_service=self.restic,
            docker_resource_args=self.docker.resource_args,
        )
