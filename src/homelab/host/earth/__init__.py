from homelab_docker.config.host import HostServiceModelConfig
from homelab_global import GlobalArgs
from homelab_network.resource.network import NetworkResource
from homelab_tailscale_service import TailscaleService
from homelab_traefik_service import TraefikService
from pulumi import ResourceOptions

from .. import HostBase
from .config import EarthServiceConfig


class EarthHost(HostBase[EarthServiceConfig]):
    def __init__(
        self,
        service: EarthServiceConfig,
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

        self.traefik = TraefikService(
            self.services_config.traefik,
            opts=self.child_opts,
            network_resource=self.network,
            extractor_args=self.extractor_args,
        )

        self.build_extra_services()

        self.build_file()

        self.register_outputs({})

    @property
    def traefik_service(self) -> TraefikService | None:
        return self.traefik
