from homelab_backup.resource import BackupResource
from homelab_ddns_service import DdnsService
from homelab_docker.config.host import HostServiceModelConfig
from homelab_global.resource import GlobalResource
from homelab_kanidm_service import KanidmService
from homelab_network.resource.network import NetworkResource
from pulumi import ResourceOptions

from .. import HostBase
from .config import SunServiceConfig


class SunHost(HostBase[SunServiceConfig]):
    def __init__(
        self,
        service: SunServiceConfig,
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

        self.ddns = DdnsService(
            self.services_config.ddns,
            opts=self.child_opts,
            network_resource=self.network,
            extractor_args=self.extractor_args,
        )
        self.kanidm = KanidmService(
            self.services_config.kanidm,
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )
