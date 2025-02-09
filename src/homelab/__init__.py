from homelab_config import Config
from homelab_docker.config.docker import DockerConfig
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
        self.docker = Docker(self.config)

        self.tailscale = TailscaleService(
            self.docker.services_config.tailscale,
            opts=None,
            hostname=Config.get_name(None, project=True, stack=True),
            container_model_global_args=self.docker.container_model_global_args,
        )

        self.network = NetworkResource(
            self.config.network,
            opts=None,
            token_name=Config.get_name(None, project=True, stack=True),
            private_ips=self.tailscale.ips,
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
