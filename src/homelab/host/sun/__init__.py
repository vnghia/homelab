from homelab_backup_service import BackupService
from homelab_balite_service import BaliteService
from homelab_barman_service import BarmanService
from homelab_crowdsec_service import CrowdsecService
from homelab_dagu_service import DaguService
from homelab_ddns_service import DdnsService
from homelab_docker.config import DockerServiceModelConfigs
from homelab_global import GlobalArgs
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
        config: SunServiceConfig,
        *,
        opts: ResourceOptions | None,
        global_args: GlobalArgs,
        network_resource: NetworkResource,
        docker_service_model_configs: DockerServiceModelConfigs,
    ) -> None:
        super().__init__(
            config,
            opts=opts,
            global_args=global_args,
            network_resource=network_resource,
            docker_service_model_configs=docker_service_model_configs,
        )

        self.tailscale = TailscaleService(
            self.services_config.tailscale,
            opts=self.child_opts,
            hostname=self.hostname,
            internal_aliases=self.network.config.aliases,
            extractor_args=self.extractor_args,
        )

        self.gluetun = GluetunService(
            self.services_config.gluetun,
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )

        self.crowdsec = CrowdsecService(
            self.services_config.crowdsec,
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )
        self.traefik = TraefikService(
            self.services_config.traefik,
            opts=self.child_opts,
            network_resource=self.network,
            extractor_args=self.extractor_args,
        )
        self.ddns = DdnsService(
            self.services_config.ddns,
            opts=self.child_opts,
            network_resource=self.network,
            extractor_args=self.extractor_args,
        )

        self.dagu = DaguService(
            self.services_config.dagu,
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )
        self.kanidm = KanidmService(
            self.services_config.kanidm,
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )
        self.ntfy = NtfyService(
            self.services_config.ntfy,
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )

        self.build_extra_services()

        # It should always be the last service
        self.barman = BarmanService(
            self.services_config.barman,
            opts=self.child_opts,
            backup_config=self.services_config.backup.config,
            extractor_args=self.extractor_args,
        )

        self.balite = BaliteService(
            self.services_config.balite,
            opts=self.child_opts,
            backup_config=self.services_config.backup.config,
            extractor_args=self.extractor_args,
        )

        self.restic = ResticService(
            self.services_config.restic,
            opts=self.child_opts,
            hostname=self.hostname,
            backup_config=self.services_config.backup.config,
            barman_service=self.barman,
            balite_service=self.balite,
            extractor_args=self.extractor_args,
        )

        self.file = File(
            opts=self.child_opts, traefik_service=self.traefik, dagu_service=self.dagu
        )

        self.backup = BackupService(
            self.services_config.backup,
            opts=self.child_opts,
            dagu_service=self.dagu,
            restic_service=self.restic,
            extractor_args=self.extractor_args,
        )

        self.register_outputs({})
