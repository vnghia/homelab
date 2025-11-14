from __future__ import annotations

from homelab_backup_service import BackupService
from homelab_balite_service import BaliteService
from homelab_barman_service import BarmanService
from homelab_dagu_service import DaguService
from homelab_docker.config.host import HostServiceModelConfig
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.host import HostResourceBase
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from homelab_global.resource import GlobalResource
from homelab_network.resource.network import NetworkResource
from homelab_restic_service import ResticService
from homelab_tailscale_service import TailscaleService
from homelab_traefik_service import TraefikService
from pulumi import ResourceOptions

from ..file import File
from .config import HostServiceConfig


class HostBaseNoConfig(HostResourceBase):
    HOST_BASES: dict[str, HostBaseNoConfig] = {}

    def __init__(
        self,
        name: str,
        *,
        opts: ResourceOptions | None,
        global_resource: GlobalResource,
        network_resource: NetworkResource,
        config: HostServiceModelConfig,
        host_services_config: HostServiceConfig,
    ) -> None:
        super().__init__(
            name=name,
            opts=opts,
            global_resource=global_resource,
            network_resource=network_resource,
            config=config,
        )

        self.host_services_config = host_services_config
        self.extra_services_config = host_services_config.extra(
            ServiceWithConfigModel[ExtraConfig]
        )
        self.HOST_BASES[self.name] = self

    def build_tailscale_service(self) -> None:
        self.tailscale = TailscaleService(
            self.host_services_config.tailscale,
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )

    def build_traefik_service(self) -> None:
        self.traefik = TraefikService(
            self.host_services_config.traefik,
            opts=self.child_opts,
            network_resource=self.network,
            extractor_args=self.extractor_args,
        )

    def build_dagu_service(self) -> None:
        self.dagu = DaguService(
            self.host_services_config.dagu,
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )

    def build_extra_service(self, service: str) -> None:
        if service in self.services:
            return

        model = self.extra_services_config[service]
        if model.depends_on:
            for depend in model.depends_on:
                depend_full = depend.to_full()
                (
                    self.HOST_BASES[depend_full.host] if depend_full.host else self
                ).build_extra_service(depend_full.service)

        type("{}Service".format(service.capitalize()), (ExtraService,), {})(
            model, opts=self.child_opts, extractor_args=self.extractor_args
        ).build()

    def build_final_services_before_file(self) -> None:
        self.barman = BarmanService(
            self.host_services_config.barman,
            opts=self.child_opts,
            backup_config=self.host_services_config.backup.config,
            extractor_args=self.extractor_args,
        )

        self.balite = BaliteService(
            self.host_services_config.balite,
            opts=self.child_opts,
            backup_config=self.host_services_config.backup.config,
            extractor_args=self.extractor_args,
        )

        self.restic = ResticService(
            self.host_services_config.restic,
            opts=self.child_opts,
            backup_config=self.host_services_config.backup.config,
            barman_service=self.barman,
            balite_service=self.balite,
            extractor_args=self.extractor_args,
        )

    def build_final_services_after_file(self) -> None:
        self.backup = BackupService(
            self.host_services_config.backup,
            opts=self.child_opts,
            dagu_service=self.dagu,
            restic_service=self.restic,
            extractor_args=self.extractor_args,
        )

    def build_file(self) -> None:
        self.file = File(
            opts=self.child_opts,
            traefik_service=self.traefik,
            dagu_service=self.dagu,
        )

    @classmethod
    def finalize(cls) -> None:
        from .sun import SunHost

        for name, host in cls.HOST_BASES.items():
            if name != SunHost.instance_name():
                host.build_dagu_service()

            for service in host.extra_services_config:
                host.build_extra_service(service)

        # Building Dagu service on Sun host last since it depends on Dagu API tokens of other hosts.
        cls.HOST_BASES[SunHost.instance_name()].build_dagu_service()

        for host in cls.HOST_BASES.values():
            host.build_final_services_before_file()
            host.build_file()
            host.build_final_services_after_file()
            host.register_outputs({})


class HostBase[T: HostServiceConfig](HostBaseNoConfig):
    def __init__(
        self,
        name: str,
        service: T,
        *,
        opts: ResourceOptions | None,
        global_resource: GlobalResource,
        network_resource: NetworkResource,
        config: HostServiceModelConfig,
    ) -> None:
        super().__init__(
            name=name,
            opts=opts,
            global_resource=global_resource,
            network_resource=network_resource,
            config=config,
            host_services_config=service,
        )

        self.services_config = service
        self.build_initial_extra_services()

        self.build_tailscale_service()
        self.build_traefik_service()

    def build_initial_extra_services(self) -> None:
        for service, model in self.services_config.services.items():
            if service in self.extra_services_config or not model.depends_on:
                continue
            for depend in model.depends_on:
                depend_full = depend.to_full()
                if depend_full.host:
                    raise ValueError(
                        "Building initial extra services does not support switching host"
                    )
                if depend_full.service not in self.extra_services_config:
                    raise ValueError(
                        "Building initial extra services only supports extra services"
                    )
                self.build_extra_service(depend_full.service)
