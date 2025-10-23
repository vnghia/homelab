from homelab_backup_service import BackupService
from homelab_balite_service import BaliteService
from homelab_barman_service import BarmanService
from homelab_crowdsec_service import CrowdsecService
from homelab_dagu_service import DaguService
from homelab_ddns_service import DdnsService
from homelab_docker.config.host import HostServiceModelConfig
from homelab_global import GlobalArgs
from homelab_gluetun_service import GluetunService
from homelab_kanidm_service import KanidmService
from homelab_network.resource.network import NetworkResource
from homelab_restic_service import ResticService
from homelab_tailscale_service import TailscaleService
from homelab_traefik_service import TraefikService
from pulumi import ResourceOptions

from .. import HostBase
from .config import SunServiceConfig


class SunHost(HostBase[SunServiceConfig]):
    def __init__(
        self,
        service: SunServiceConfig,
        *,
        opts: ResourceOptions | None,
        global_args: GlobalArgs,
        network_resource: NetworkResource,
        config: HostServiceModelConfig,
    ) -> None:
        super().__init__(
            service,
            opts=opts,
            global_args=global_args,
            network_resource=network_resource,
            config=config,
        )

        self.tailscale = TailscaleService(
            self.services_config.tailscale,
            opts=self.child_opts,
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

    def build_final_services_before_file(self) -> None:
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
            backup_config=self.services_config.backup.config,
            barman_service=self.barman,
            balite_service=self.balite,
            extractor_args=self.extractor_args,
        )

    def build_final_services_after_file(self) -> None:
        self.backup = BackupService(
            self.services_config.backup,
            opts=self.child_opts,
            dagu_service=self.dagu,
            restic_service=self.restic,
            extractor_args=self.extractor_args,
        )

    @property
    def traefik_service(self) -> TraefikService | None:
        return self.traefik

    @property
    def dagu_service(self) -> DaguService | None:
        return self.dagu
