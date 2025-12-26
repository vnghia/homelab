from homelab_backup.config import BackupHostConfig
from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import LitestreamConfig


class LitestreamService(ServiceWithConfigResourceBase[LitestreamConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[LitestreamConfig],
        *,
        opts: ResourceOptions,
        backup_host_config: BackupHostConfig,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.build_containers()

        self.register_outputs({})
