from homelab_backup.resource import BackupResource
from homelab_docker.config.host import HostServiceModelConfig
from homelab_global.resource import GlobalResource
from homelab_network.resource.network import NetworkResource
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
        global_resource: GlobalResource,
        backup_resource: BackupResource,
        network_resource: NetworkResource,
        config: HostServiceModelConfig,
    ) -> None:
        super().__init__(
            self.instance_name(),
            service,
            opts=opts,
            global_resource=global_resource,
            backup_resource=backup_resource,
            network_resource=network_resource,
            config=config,
        )

    @property
    def traefik_service(self) -> TraefikService | None:
        return self.traefik
